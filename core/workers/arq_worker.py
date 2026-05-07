"""Arq worker for executing persisted agent tasks."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from arq.connections import RedisSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker
from sqlalchemy.orm import selectinload

from mycelium.agents.registry import create_agent
from mycelium.db.connection import get_engine
from mycelium.db.models import AgentStatus, Task, TaskState


async def run_agent_task(ctx: dict[str, Any], task_id: str) -> None:
    """Execute one task row through its agent implementation."""

    sessionmaker: async_sessionmaker[AsyncSession] = ctx["sessionmaker"]
    async with sessionmaker() as session:
        task = (
            await session.execute(
                select(Task).options(selectinload(Task.agent)).where(Task.id == UUID(task_id))
            )
        ).scalar_one_or_none()
        if task is None:
            return
        agent = task.agent
        agent.status = AgentStatus.busy
        agent.last_heartbeat_at = datetime.now(timezone.utc)
        task.state = TaskState.running
        task.started_at = datetime.now(timezone.utc)
        await session.commit()

        impl = create_agent(agent)
        try:
            result = await impl.run_step(task.payload_jsonb)
            task.result_jsonb = result.data
            task.tokens_used = result.tokens_used
            task.state = TaskState.complete
            agent.status = AgentStatus.idle
        except Exception as exc:
            task.error_text = str(exc)
            task.state = TaskState.failed
            agent.status = AgentStatus.errored
        finally:
            task.completed_at = datetime.now(timezone.utc)
            await session.commit()


async def startup(ctx: dict[str, Any]) -> None:
    """Initialize SQLAlchemy resources for the worker process."""

    database_url = os.environ.get(
        "DATABASE_URL",
        "postgresql+asyncpg://mycelium:mycelium@localhost:5432/mycelium",
    )
    engine = get_engine(database_url)
    ctx["engine"] = engine
    ctx["sessionmaker"] = async_sessionmaker(engine, expire_on_commit=False)


async def shutdown(ctx: dict[str, Any]) -> None:
    """Dispose process-local resources."""

    await ctx["engine"].dispose()


def _redis_settings() -> RedisSettings:
    dsn = os.environ.get("REDIS_URL", "redis://localhost:6379/0")
    return RedisSettings.from_dsn(dsn)


class WorkerSettings:
    """Arq CLI entry point: ``arq mycelium.core.workers.arq_worker.WorkerSettings``."""

    functions = [run_agent_task]
    redis_settings = _redis_settings()
    on_startup = startup
    on_shutdown = shutdown
    poll_delay = 0.5
    max_jobs = 4
