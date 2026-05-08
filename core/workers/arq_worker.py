"""Arq worker for executing persisted agent tasks."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

import redis.asyncio as aioredis
import structlog
from arq.connections import RedisSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from mycelium.agents.base import AgentResult, BaseAgent
from mycelium.agents.registry import create_agent, create_agent_from_values
from mycelium.bus.envelope import Envelope
from mycelium.bus.publisher import BusPublisher
from mycelium.bus.subscriber import BusSubscriber
from mycelium.core.llm.anthropic_provider import AnthropicProvider
from mycelium.core.settings import Settings
from mycelium.db.connection import get_engine
from mycelium.db.models import (
    Agent,
    AgentConfigVersion,
    AgentStatus,
    Task,
    TaskScore,
    TaskState,
    TokenLedger,
)
from mycelium.db.repos.runs import RunRepo


async def run_agent_task(
    ctx: dict[str, Any],
    task_id: str,
    replay: bool = False,
    config_version_id: str | None = None,
    experiment_id: str | None = None,
) -> None:
    """Execute one task row through its agent implementation."""

    sessionmaker: async_sessionmaker[AsyncSession] = ctx["sessionmaker"]
    bus: BusPublisher = ctx["bus"]
    subscriber: BusSubscriber = ctx["subscriber"]
    llm: AnthropicProvider = ctx["llm"]
    async with sessionmaker() as session:
        task = (
            await session.execute(
                select(Task).options(selectinload(Task.agent)).where(Task.id == UUID(task_id))
            )
        ).scalar_one_or_none()
        if task is None:
            return
        agent = task.agent
        config_version = await _resolve_config_version(session, task, agent, config_version_id)
        with structlog.contextvars.bound_contextvars(
            task_id=str(task.id),
            agent_id=str(agent.id),
        ):
            if replay:
                await _run_replay(
                    session=session,
                    sessionmaker=sessionmaker,
                    bus=bus,
                    subscriber=subscriber,
                    llm=llm,
                    task=task,
                    agent=agent,
                    config_version=config_version,
                    experiment_id=experiment_id,
                )
            else:
                await _run_live_task(
                    session=session,
                    sessionmaker=sessionmaker,
                    bus=bus,
                    subscriber=subscriber,
                    llm=llm,
                    task=task,
                    agent=agent,
                    config_version=config_version,
                )


async def _resolve_config_version(
    session: AsyncSession,
    task: Task,
    agent: Agent,
    override_id: str | None,
) -> AgentConfigVersion | None:
    if override_id is not None:
        return await session.get(AgentConfigVersion, UUID(override_id))
    if task.config_version_id is not None:
        return await session.get(AgentConfigVersion, task.config_version_id)
    if agent.current_version_id is not None:
        return await session.get(AgentConfigVersion, agent.current_version_id)
    return None


async def _run_live_task(
    *,
    session: AsyncSession,
    sessionmaker: async_sessionmaker[AsyncSession],
    bus: BusPublisher,
    subscriber: BusSubscriber,
    llm: AnthropicProvider,
    task: Task,
    agent: Agent,
    config_version: AgentConfigVersion | None,
) -> None:
    agent.status = AgentStatus.busy
    agent.last_heartbeat_at = datetime.now(timezone.utc)
    task.state = TaskState.running
    task.started_at = datetime.now(timezone.utc)
    if task.config_version_id is None and config_version is not None:
        task.config_version_id = config_version.id
    await session.commit()
    await bus.publish(
        Envelope(
            channel="kernel.events",
            message_type="system",
            to_agent=agent.id,
            payload={
                "event": "task.started",
                "task_id": str(task.id),
                "agent_id": str(agent.id),
            },
        )
    )

    impl = _create_impl(agent, config_version)
    impl.bind(llm=llm, bus=bus, subscriber=subscriber, sessionmaker=sessionmaker)
    try:
        result = await impl.run_step(task.payload_jsonb)
        token_total = _token_total(result)
        task.result_jsonb = result.data
        task.tokens_used = token_total
        task.state = TaskState.complete
        agent.status = AgentStatus.idle
        agent.tokens_used_today += token_total
        _add_token_ledger_rows(session, result, agent.id, task.id)
        _add_score_rows(session, result, agent.id, task.id)
    except Exception as exc:
        task.error_text = str(exc)
        task.state = TaskState.failed
        agent.status = AgentStatus.errored
    finally:
        task.completed_at = datetime.now(timezone.utc)
        await session.commit()
        await bus.publish(
            Envelope(
                channel="kernel.events",
                message_type="system",
                to_agent=agent.id,
                payload={
                    "event": (
                        "task.completed" if task.state == TaskState.complete else "task.failed"
                    ),
                    "task_id": str(task.id),
                    "agent_id": str(agent.id),
                    "state": task.state.value,
                    "result": task.result_jsonb,
                    "error": task.error_text,
                },
            )
        )
        reply = _completion_reply_envelope(task, agent)
        if reply is not None:
            await bus.publish(reply)


async def _run_replay(
    *,
    session: AsyncSession,
    sessionmaker: async_sessionmaker[AsyncSession],
    bus: BusPublisher,
    subscriber: BusSubscriber,
    llm: AnthropicProvider,
    task: Task,
    agent: Agent,
    config_version: AgentConfigVersion | None,
    experiment_id: str | None,
) -> None:
    run_repo = RunRepo(session)
    run = await run_repo.create(
        experiment_id=UUID(experiment_id) if experiment_id is not None else None,
        source_task_id=task.id,
        agent_id=agent.id,
        config_version_id=config_version.id if config_version is not None else None,
        state="running",
    )
    await session.commit()

    impl = _create_impl(agent, config_version)
    impl.bind(llm=llm, bus=bus, subscriber=subscriber, sessionmaker=sessionmaker)
    try:
        result = await impl.run_step(task.payload_jsonb)
        await run_repo.complete(run, result=result.data, tokens_used=_token_total(result))
    except Exception as exc:
        await run_repo.fail(run, error=str(exc))
    finally:
        await session.commit()


def _create_impl(agent: Agent, config_version: AgentConfigVersion | None) -> BaseAgent:
    if config_version is None:
        return create_agent(agent)
    return create_agent_from_values(
        agent_id=agent.id,
        name=agent.name,
        agent_type=agent.type,
        system_prompt=config_version.system_prompt,
        model=config_version.model,
        config=config_version.config_jsonb,
    )


def _token_total(result: AgentResult) -> int:
    return result.tokens_used or sum(call.total_tokens for call in result.llm_calls)


def _completion_reply_envelope(task: Task, agent: Agent) -> Envelope | None:
    """Build the direct reply a waiting parent agent consumes, if requested."""

    if task.reply_to_agent_id is None or task.completion_correlation_id is None:
        return None
    return Envelope(
        from_agent=agent.id,
        to_agent=task.reply_to_agent_id,
        channel=f"agent.{task.reply_to_agent_id}.inbox",
        message_type="reply",
        correlation_id=task.completion_correlation_id,
        payload={
            "event": "task.completed" if task.state == TaskState.complete else "task.failed",
            "task_id": str(task.id),
            "agent_id": str(agent.id),
            "parent_task_id": str(task.parent_task_id) if task.parent_task_id else None,
            "state": task.state.value,
            "result": task.result_jsonb,
            "error": task.error_text,
        },
    )


def _add_token_ledger_rows(
    session: AsyncSession,
    result: AgentResult,
    agent_id: UUID,
    task_id: UUID,
) -> None:
    for call in result.llm_calls:
        session.add(
            TokenLedger(
                agent_id=agent_id,
                task_id=task_id,
                model=call.model,
                tokens_in=call.input_tokens,
                tokens_out=call.output_tokens,
                cache_read_tokens=call.cache_read_tokens,
                cache_write_tokens=call.cache_write_tokens,
                cost_micros=0,
            )
        )


def _add_score_rows(
    session: AsyncSession,
    result: AgentResult,
    agent_id: UUID,
    task_id: UUID,
) -> None:
    scores = {
        "self": result.self_score,
        "reviewer": result.reviewer_score,
    }
    for score_kind, score in scores.items():
        if score is None:
            continue
        session.add(
            TaskScore(
                id=uuid4(),
                task_id=task_id,
                scorer_agent_id=agent_id,
                score_kind=score_kind,
                score=score,
            )
        )


async def startup(ctx: dict[str, Any]) -> None:
    """Initialize SQLAlchemy resources for the worker process."""

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://mycelium:mycelium@localhost:5432/mycelium",
    )
    redis_url = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    settings = Settings(database_url=database_url, redis_url=redis_url)
    engine = get_engine(database_url)
    redis: aioredis.Redis = aioredis.from_url(redis_url, decode_responses=True)  # type: ignore[no-untyped-call]
    ctx["engine"] = engine
    ctx["sessionmaker"] = async_sessionmaker(engine, expire_on_commit=False)
    ctx["redis"] = redis
    ctx["bus"] = BusPublisher(redis, sessionmaker=ctx["sessionmaker"])
    ctx["subscriber"] = BusSubscriber(redis)
    ctx["llm"] = AnthropicProvider(settings)


async def shutdown(ctx: dict[str, Any]) -> None:
    """Dispose process-local resources."""

    await ctx["redis"].aclose()
    await ctx["engine"].dispose()


def _redis_settings() -> RedisSettings:
    dsn = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return RedisSettings.from_dsn(dsn)


class WorkerSettings:
    """Arq CLI entry point: ``arq mycelium.core.workers.arq_worker.WorkerSettings``."""

    functions = [run_agent_task]
    redis_settings = _redis_settings()
    queue_name = os.environ.get("ARQ_QUEUE_NAME", "mycelium:arq")
    on_startup = startup
    on_shutdown = shutdown
    poll_delay = 0.5
    max_jobs = 4
