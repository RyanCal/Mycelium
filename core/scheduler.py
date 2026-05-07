"""Priority scheduler backed by Postgres rows and Arq jobs."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

import structlog
from arq import ArqRedis
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from mycelium.db.models import Task, TaskState


class TaskSpec(BaseModel):
    """Public task input before it becomes a persisted ``Task`` row."""

    payload: dict[str, Any]
    estimated_tokens: int = Field(default=4000, ge=0)
    parent_task_id: UUID | None = None
    deadline: datetime | None = None


class Scheduler:
    """Moves queued tasks from durable storage into Arq."""

    def __init__(
        self,
        arq_pool: ArqRedis,
        sessionmaker: async_sessionmaker[AsyncSession],
        *,
        queue_name: str = "mycelium:arq",
    ) -> None:
        self._arq = arq_pool
        self._sessionmaker = sessionmaker
        self._queue_name = queue_name

    async def enqueue(self, task_id: UUID, priority: int) -> str | None:
        """Enqueue a task execution job and persist the Arq job id when available."""

        job = await self._arq.enqueue_job(
            "run_agent_task",
            str(task_id),
            _queue_name=self._queue_name,
            _defer_by=max(0, 100 - priority) / 1000,
        )
        job_id = getattr(job, "job_id", None)
        if job_id is not None:
            async with self._sessionmaker() as session:
                db_task = await session.get(Task, task_id)
                if db_task is not None:
                    db_task.state = TaskState.dispatched
                    db_task.arq_job_id = job_id
                    await session.commit()
        return job_id

    async def tick(self) -> UUID | None:
        """Dispatch the highest-priority queued task if one exists."""

        async with self._sessionmaker() as session:
            stmt = (
                select(Task)
                .where(Task.state == TaskState.queued)
                .order_by(Task.priority.desc(), Task.created_at.asc())
                .limit(1)
                .with_for_update(skip_locked=True)
            )
            task = (await session.execute(stmt)).scalar_one_or_none()
            if task is None:
                return None
            task_id = task.id
            priority = task.priority

        with structlog.contextvars.bound_contextvars(task_id=str(task_id)):
            await self.enqueue(task_id, priority)
        return task_id

    async def complete_task(
        self,
        task_id: UUID,
        *,
        result: dict[str, Any] | None = None,
        error: str | None = None,
        tokens_used: int = 0,
    ) -> None:
        """Mark a task complete or failed after a worker/sandbox result."""

        async with self._sessionmaker() as session:
            task = await session.get(Task, task_id)
            if task is None:
                return
            task.result_jsonb = result
            task.error_text = error
            task.tokens_used = tokens_used
            task.completed_at = datetime.now(timezone.utc)
            task.state = TaskState.failed if error else TaskState.complete
            await session.commit()

    async def drain(self, timeout: float) -> None:
        """Wait for dispatched or running work to finish until timeout expires."""

        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while loop.time() < deadline:
            async with self._sessionmaker() as session:
                count = (
                    await session.execute(
                        select(func.count(Task.id)).where(
                            Task.state.in_([TaskState.dispatched, TaskState.running])
                        )
                    )
                ).scalar_one()
            if count == 0:
                return
            await asyncio.sleep(min(0.5, max(0.0, deadline - loop.time())))
