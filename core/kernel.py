"""kernel.py - The Mycelium Kernel.

The Kernel is the central orchestrator: it owns the agent registry, task
scheduler, context-budget ledger, and bus subscription multiplexer. Everything
else (FastAPI handlers, Arq workers, sandbox manager) is a satellite that holds
a reference to one Kernel instance and calls into its public methods.

Key design choice: the kernel does not execute agent steps in-process. It
dispatches them to Arq workers. This keeps the kernel responsive; a single bad
agent that hangs in an LLM call cannot block the scheduler tick.
"""

from __future__ import annotations

import asyncio
import logging
from contextlib import suppress
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import redis.asyncio as aioredis
from arq import ArqRedis
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker

from mycelium.agents.spec import AgentSpec
from mycelium.bus.envelope import Envelope
from mycelium.bus.publisher import BusPublisher
from mycelium.bus.subscriber import BusSubscriber
from mycelium.core.context_budget import BudgetExceeded, ContextBudget
from mycelium.core.exceptions import AgentNotFound, TaskNotFound
from mycelium.core.scheduler import Scheduler, TaskSpec
from mycelium.core.settings import Settings
from mycelium.db.models import Agent, AgentConfigVersion, AgentStatus, CommsLog, Task, TaskState

logger = logging.getLogger(__name__)


class Kernel:
    """The headless resource manager for Mycelium."""

    TICK_INTERVAL_SECONDS = 0.5
    HEARTBEAT_INTERVAL_SECONDS = 5.0

    def __init__(
        self,
        settings: Settings,
        engine: AsyncEngine,
        redis: aioredis.Redis,
        arq_pool: ArqRedis,
    ) -> None:
        self.settings = settings
        self.started_at = datetime.now(timezone.utc)
        self._engine = engine
        self._sessionmaker = async_sessionmaker(engine, expire_on_commit=False)
        self._redis = redis
        self._arq = arq_pool
        self._publisher = BusPublisher(redis, sessionmaker=self._sessionmaker)
        self._subscriber = BusSubscriber(redis)
        self._scheduler = Scheduler(
            arq_pool,
            self._sessionmaker,
            queue_name=settings.arq_queue_name,
        )
        self._budget = ContextBudget(self._sessionmaker)
        self._stop = asyncio.Event()
        self._tasks: list[asyncio.Task[None]] = []

    @property
    def sessionmaker(self) -> async_sessionmaker[AsyncSession]:
        """Expose short-lived DB sessions to API dependencies."""

        return self._sessionmaker

    async def register_agent(self, spec: AgentSpec) -> UUID:
        """Persist an agent record and announce registration on the bus.

        Registration is idempotent on ``spec.name`` so prompt reloads can update
        mutable fields without losing task or comms history.
        """

        async with self._sessionmaker() as session:
            existing = (
                await session.execute(select(Agent).where(Agent.name == spec.name))
            ).scalar_one_or_none()

            if existing:
                config_changed = (
                    existing.system_prompt != spec.system_prompt
                    or existing.model != spec.model
                    or existing.config_jsonb != spec.config
                )
                existing.system_prompt = spec.system_prompt
                existing.model = spec.model
                existing.config_jsonb = spec.config
                existing.type = spec.type
                existing.token_budget_daily = spec.token_budget_daily
                agent_id = existing.id
                if config_changed or existing.current_version_id is None:
                    await self._write_agent_config_version(
                        session,
                        existing,
                        reason="manual_edit" if config_changed else "registered",
                        created_by="kernel",
                    )
                logger.info(
                    "agent.updated",
                    extra={"agent_id": str(agent_id), "agent_name": spec.name},
                )
            else:
                agent = Agent(
                    id=uuid4(),
                    name=spec.name,
                    type=spec.type,
                    status=AgentStatus.idle,
                    system_prompt=spec.system_prompt,
                    model=spec.model,
                    config_jsonb=spec.config,
                    token_budget_daily=spec.token_budget_daily,
                    tokens_used_today=0,
                )
                session.add(agent)
                await session.flush()
                await self._write_agent_config_version(
                    session,
                    agent,
                    reason="registered",
                    created_by="kernel",
                )
                agent_id = agent.id
                logger.info(
                    "agent.registered",
                    extra={"agent_id": str(agent_id), "agent_name": spec.name},
                )

            await session.commit()

        await self._publisher.publish(
            Envelope(
                from_agent=None,
                to_agent=None,
                channel="kernel.events",
                message_type="system",
                payload={
                    "event": "agent.registered",
                    "agent_id": str(agent_id),
                    "name": spec.name,
                },
            )
        )
        return agent_id

    async def list_agents(self) -> list[dict[str, Any]]:
        """Return API-ready agent summaries."""

        async with self._sessionmaker() as session:
            agents = (
                await session.execute(select(Agent).order_by(Agent.created_at.asc()))
            ).scalars()
            return [self._serialize_agent(agent) for agent in agents]

    async def get_agent(self, agent_id: UUID) -> dict[str, Any]:
        """Return one API-ready agent detail."""

        async with self._sessionmaker() as session:
            agent = await session.get(Agent, agent_id)
            if agent is None:
                raise AgentNotFound(agent_id)
            return self._serialize_agent(agent)

    async def dispatch_task(self, agent_id: UUID, task: TaskSpec, priority: int = 50) -> UUID:
        """Enqueue a task for an agent and return the persisted task id immediately."""

        async with self._sessionmaker() as session:
            agent = await session.get(Agent, agent_id)
            if agent is None:
                raise AgentNotFound(agent_id)

            if agent.current_version_id is None:
                await self._write_agent_config_version(
                    session,
                    agent,
                    reason="registered",
                    created_by="kernel",
                )

            await self._check_context_budget(agent, task.estimated_tokens, session)

            scored = self._score_priority(priority, task)
            db_task = Task(
                id=uuid4(),
                agent_id=agent_id,
                parent_task_id=task.parent_task_id,
                reply_to_agent_id=task.reply_to_agent_id,
                completion_correlation_id=task.completion_correlation_id,
                config_version_id=agent.current_version_id,
                priority=scored,
                state=TaskState.queued,
                payload_jsonb=task.payload,
                token_budget=task.estimated_tokens,
                tokens_used=0,
            )
            session.add(db_task)
            await session.commit()
            await session.refresh(db_task)

        await self._scheduler.enqueue(db_task.id, scored)
        await self._publisher.publish(
            Envelope(
                from_agent=None,
                to_agent=agent_id,
                channel="kernel.events",
                message_type="system",
                payload={
                    "event": "task.dispatched",
                    "task_id": str(db_task.id),
                    "agent_id": str(agent_id),
                    "priority": scored,
                },
            )
        )
        logger.info(
            "task.dispatched",
            extra={"task_id": str(db_task.id), "agent_id": str(agent_id), "priority": scored},
        )
        return db_task.id

    async def list_tasks(
        self,
        *,
        state: TaskState | None = None,
        agent_id: UUID | None = None,
    ) -> list[dict[str, Any]]:
        """Return API-ready tasks filtered by optional state/agent."""

        async with self._sessionmaker() as session:
            stmt = select(Task).order_by(Task.created_at.desc())
            if state is not None:
                stmt = stmt.where(Task.state == state)
            if agent_id is not None:
                stmt = stmt.where(Task.agent_id == agent_id)
            tasks = (await session.execute(stmt)).scalars()
            return [self._serialize_task(task) for task in tasks]

    async def get_task(self, task_id: UUID) -> dict[str, Any]:
        """Return one API-ready task detail."""

        async with self._sessionmaker() as session:
            task = await session.get(Task, task_id)
            if task is None:
                raise TaskNotFound(task_id)
            return self._serialize_task(task)

    async def log_comms(self, envelope: Envelope) -> None:
        """Persist an envelope to ``comms_log`` without publishing it."""

        async with self._sessionmaker() as session:
            session.add(
                CommsLog(
                    id=uuid4(),
                    envelope_id=envelope.id,
                    from_agent=envelope.from_agent,
                    to_agent=envelope.to_agent,
                    channel=envelope.channel,
                    message_type=envelope.message_type,
                    payload_jsonb=envelope.payload,
                    reply_to_envelope_id=envelope.reply_to,
                    created_at=envelope.ts,
                )
            )
            await session.commit()

    async def health(self) -> dict[str, Any]:
        """Return lightweight daemon health for the API health route."""

        redis_ok = False
        with suppress(Exception):
            redis_ok = bool(await self._redis.ping())

        async with self._sessionmaker() as session:
            agent_count = int((await session.execute(select(func.count(Agent.id)))).scalar_one())

        return {
            "status": "ok" if redis_ok else "degraded",
            "app": self.settings.app_name,
            "environment": self.settings.environment,
            "uptime_seconds": int((datetime.now(timezone.utc) - self.started_at).total_seconds()),
            "agent_count": agent_count,
            "redis": "ok" if redis_ok else "unavailable",
        }

    async def start_daemon(self) -> None:
        """Bring up tick loop, bus subscription, and heartbeat until stopped."""

        logger.info("kernel.starting")
        self._tasks = [
            asyncio.create_task(self._tick_loop(), name="kernel.tick"),
            asyncio.create_task(self._bus_loop(), name="kernel.bus"),
            asyncio.create_task(self._heartbeat_loop(), name="kernel.heartbeat"),
        ]
        await self._stop.wait()

    async def stop_daemon(self, drain_seconds: float = 30.0) -> None:
        """Graceful shutdown: stop accepting new work, drain, then cancel loops."""

        if self._stop.is_set():
            return
        logger.info("kernel.stopping")
        self._stop.set()
        await self._scheduler.drain(timeout=drain_seconds)
        for task in self._tasks:
            task.cancel()
        for task in self._tasks:
            with suppress(asyncio.CancelledError):
                await task
        await self._redis.aclose()
        await self._engine.dispose()
        logger.info("kernel.stopped")

    async def _tick_loop(self) -> None:
        """Main scheduler tick. Pulls highest-priority queued task and dispatches."""

        while not self._stop.is_set():
            try:
                await self._scheduler.tick()
            except Exception:
                logger.exception("kernel.tick_failed")
            await asyncio.sleep(self.TICK_INTERVAL_SECONDS)

    async def _bus_loop(self) -> None:
        """Listen on kernel-level channels."""

        async for envelope in self._subscriber.subscribe(
            ["kernel.commands", "kernel.events", "sandbox.*.results"],
            stop=self._stop,
        ):
            if self._stop.is_set():
                break
            try:
                await self._handle_bus_event(envelope)
            except Exception:
                logger.exception(
                    "kernel.bus_handler_failed",
                    extra={"envelope_id": str(envelope.id)},
                )

    async def _heartbeat_loop(self) -> None:
        """Mark busy agents stale if their heartbeat stops moving."""

        while not self._stop.is_set():
            cutoff = datetime.now(timezone.utc).timestamp() - 3 * self.HEARTBEAT_INTERVAL_SECONDS
            async with self._sessionmaker() as session:
                await session.execute(
                    update(Agent)
                    .where(
                        Agent.last_heartbeat_at < datetime.fromtimestamp(cutoff, tz=timezone.utc),
                        Agent.status == AgentStatus.busy,
                    )
                    .values(status=AgentStatus.errored)
                )
                await session.commit()
            await asyncio.sleep(self.HEARTBEAT_INTERVAL_SECONDS)

    def _score_priority(self, raw: int, task: TaskSpec) -> int:
        """Combine caller priority with simple kernel-side weights."""

        score = max(0, min(100, raw))
        if task.parent_task_id is not None:
            score += 5
        if task.deadline is not None:
            mins = max(0.0, (task.deadline - datetime.now(timezone.utc)).total_seconds() / 60.0)
            score += min(30, int(round(60 / max(1.0, mins))))
        return min(100, score)

    async def _check_context_budget(
        self,
        agent: Agent,
        requested: int,
        session: AsyncSession,
    ) -> None:
        """Reject dispatch when an agent would exceed its daily token budget."""

        if agent.token_budget_daily is None:
            return
        used = await self._budget.tokens_used_today(agent.id, session)
        if used + requested > agent.token_budget_daily:
            raise BudgetExceeded(
                agent_id=agent.id,
                used=used,
                requested=requested,
                budget=agent.token_budget_daily,
            )

    async def _handle_bus_event(self, envelope: Envelope) -> None:
        """React to kernel-level bus events."""

        event = envelope.payload.get("event")
        if envelope.channel.startswith("sandbox.") and envelope.channel.endswith(".results"):
            await self._scheduler.complete_task(
                task_id=UUID(envelope.payload["task_id"]),
                result=envelope.payload.get("result"),
                error=envelope.payload.get("error"),
                tokens_used=envelope.payload.get("tokens_used", 0),
            )
        elif event == "subagent.requested":
            await self._spawn_subagent(envelope)

    async def _spawn_subagent(self, envelope: Envelope) -> tuple[UUID, UUID]:
        """Materialize a sub-agent triggered by another agent."""

        spec = AgentSpec(**envelope.payload["spec"])
        agent_id = await self.register_agent(spec)
        task_payload = dict(envelope.payload["task"])
        parent_task_id = envelope.payload.get("parent_task_id")
        if parent_task_id is not None and task_payload.get("parent_task_id") is None:
            task_payload["parent_task_id"] = (
                parent_task_id if isinstance(parent_task_id, UUID) else UUID(str(parent_task_id))
            )
        if envelope.from_agent is not None:
            task_payload["reply_to_agent_id"] = envelope.from_agent
        if envelope.correlation_id is not None:
            task_payload["completion_correlation_id"] = envelope.correlation_id
        task = TaskSpec(**task_payload)
        task_id = await self.dispatch_task(
            agent_id,
            task,
            priority=envelope.payload.get("priority", 60),
        )
        return agent_id, task_id

    def _serialize_agent(self, agent: Agent) -> dict[str, Any]:
        return {
            "id": str(agent.id),
            "name": agent.name,
            "type": agent.type,
            "status": agent.status.value,
            "system_prompt": agent.system_prompt,
            "model": agent.model,
            "config_jsonb": agent.config_jsonb,
            "sandbox_container_id": agent.sandbox_container_id,
            "token_budget_daily": agent.token_budget_daily,
            "tokens_used_today": agent.tokens_used_today,
            "current_version_id": (
                str(agent.current_version_id) if agent.current_version_id else None
            ),
            "last_heartbeat_at": self._iso(agent.last_heartbeat_at),
            "created_at": self._iso(agent.created_at),
            "updated_at": self._iso(agent.updated_at),
        }

    def _serialize_task(self, task: Task) -> dict[str, Any]:
        return {
            "id": str(task.id),
            "agent_id": str(task.agent_id),
            "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None,
            "reply_to_agent_id": str(task.reply_to_agent_id) if task.reply_to_agent_id else None,
            "completion_correlation_id": (
                str(task.completion_correlation_id) if task.completion_correlation_id else None
            ),
            "config_version_id": str(task.config_version_id) if task.config_version_id else None,
            "priority": task.priority,
            "state": task.state.value,
            "payload_jsonb": task.payload_jsonb,
            "result_jsonb": task.result_jsonb,
            "error_text": task.error_text,
            "token_budget": task.token_budget,
            "tokens_used": task.tokens_used,
            "arq_job_id": task.arq_job_id,
            "started_at": self._iso(task.started_at),
            "completed_at": self._iso(task.completed_at),
            "created_at": self._iso(task.created_at),
            "updated_at": self._iso(task.updated_at),
        }

    def _iso(self, value: datetime | None) -> str | None:
        return value.isoformat() if value is not None else None

    async def _write_agent_config_version(
        self,
        session: AsyncSession,
        agent: Agent,
        *,
        reason: str,
        created_by: str,
    ) -> AgentConfigVersion:
        """Snapshot the mutable config that a task can later replay against."""

        latest_version = (
            await session.execute(
                select(func.max(AgentConfigVersion.version)).where(
                    AgentConfigVersion.agent_id == agent.id
                )
            )
        ).scalar_one()
        config_version = AgentConfigVersion(
            id=uuid4(),
            agent_id=agent.id,
            version=(latest_version or 0) + 1,
            system_prompt=agent.system_prompt,
            model=agent.model,
            config_jsonb=agent.config_jsonb,
            reason=reason,
            created_by=created_by,
        )
        session.add(config_version)
        await session.flush()
        agent.current_version_id = config_version.id
        return config_version
