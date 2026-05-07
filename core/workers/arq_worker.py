"""Arq worker for executing persisted agent tasks."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import redis.asyncio as aioredis
import structlog
from arq.connections import RedisSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from mycelium.agents.registry import create_agent
from mycelium.bus.envelope import Envelope
from mycelium.bus.publisher import BusPublisher
from mycelium.core.llm.anthropic_provider import AnthropicProvider
from mycelium.core.settings import Settings
from mycelium.db.connection import get_engine
from mycelium.db.models import AgentStatus, Task, TaskState, TokenLedger


async def run_agent_task(ctx: dict[str, Any], task_id: str) -> None:
    """Execute one task row through its agent implementation."""

    sessionmaker: async_sessionmaker[AsyncSession] = ctx["sessionmaker"]
    bus: BusPublisher = ctx["bus"]
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
        with structlog.contextvars.bound_contextvars(
            task_id=str(task.id),
            agent_id=str(agent.id),
        ):
            agent.status = AgentStatus.busy
            agent.last_heartbeat_at = datetime.now(timezone.utc)
            task.state = TaskState.running
            task.started_at = datetime.now(timezone.utc)
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

            impl = create_agent(agent)
            impl.bind(llm=llm, bus=bus, sessionmaker=sessionmaker)
            try:
                result = await impl.run_step(task.payload_jsonb)
                token_total = result.tokens_used or sum(
                    call.total_tokens for call in result.llm_calls
                )
                task.result_jsonb = result.data
                task.tokens_used = token_total
                task.state = TaskState.complete
                agent.status = AgentStatus.idle
                agent.tokens_used_today += token_total
                for call in result.llm_calls:
                    session.add(
                        TokenLedger(
                            agent_id=agent.id,
                            task_id=task.id,
                            model=call.model,
                            tokens_in=call.input_tokens,
                            tokens_out=call.output_tokens,
                            cache_read_tokens=call.cache_read_tokens,
                            cache_write_tokens=call.cache_write_tokens,
                            cost_micros=0,
                        )
                    )
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
                            "event": "task.completed"
                            if task.state == TaskState.complete
                            else "task.failed",
                            "task_id": str(task.id),
                            "agent_id": str(agent.id),
                            "state": task.state.value,
                            "result": task.result_jsonb,
                            "error": task.error_text,
                        },
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
