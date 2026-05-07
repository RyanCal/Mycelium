"""Repository helpers for experiment rows."""

from __future__ import annotations

from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from mycelium.db.models import Experiment


class ExperimentRepo:
    """Small persistence seam for Phase 3 experiment orchestration."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def create(
        self,
        *,
        agent_id: UUID,
        name: str,
        hypothesis: str,
        candidate_config: dict[str, Any],
        state: str = "draft",
    ) -> Experiment:
        """Create an experiment draft."""

        experiment = Experiment(
            id=uuid4(),
            agent_id=agent_id,
            name=name,
            hypothesis=hypothesis,
            candidate_config_jsonb=candidate_config,
            state=state,
        )
        self.session.add(experiment)
        await self.session.flush()
        return experiment

    async def get(self, experiment_id: UUID) -> Experiment | None:
        """Return one experiment by id."""

        return await self.session.get(Experiment, experiment_id)

    async def list_for_agent(self, agent_id: UUID) -> list[Experiment]:
        """List experiments for one agent."""

        result = await self.session.execute(
            select(Experiment)
            .where(Experiment.agent_id == agent_id)
            .order_by(Experiment.created_at.desc())
        )
        return list(result.scalars())
