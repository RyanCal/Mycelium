"""Repository helpers for replay and experiment run rows."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mycelium.db.models import Run


class RunRepo:
    """Small persistence seam for replay outputs."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        source_task_id: UUID | None,
        agent_id: UUID | None,
        config_version_id: UUID | None,
        experiment_id: UUID | None = None,
        state: str = "queued",
    ) -> Run:
        """Create a run shell before replay execution."""

        run = Run(
            id=uuid4(),
            experiment_id=experiment_id,
            source_task_id=source_task_id,
            agent_id=agent_id,
            config_version_id=config_version_id,
            state=state,
            tokens_used=0,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def complete(
        self,
        run: Run,
        *,
        result: dict[str, Any],
        tokens_used: int,
    ) -> Run:
        """Mark a replay run complete."""

        run.result_jsonb = result
        run.tokens_used = tokens_used
        run.state = "complete"
        await self.session.flush()
        return run

    async def fail(self, run: Run, *, error: str) -> Run:
        """Mark a replay run failed."""

        run.error_text = error
        run.state = "failed"
        await self.session.flush()
        return run

    async def list_for_experiment(self, experiment_id: UUID) -> list[Run]:
        """List runs for one experiment."""

        result = await self.session.execute(
            select(Run).where(Run.experiment_id == experiment_id).order_by(Run.created_at.desc())
        )
        return list(result.scalars())
