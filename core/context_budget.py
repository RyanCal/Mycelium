"""Token budget accounting for always-on agents."""

from __future__ import annotations

from datetime import datetime, time, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from mycelium.core.exceptions import KernelError
from mycelium.db.models import TokenLedger


class BudgetExceeded(KernelError):
    """Raised when dispatch would exceed an agent's daily token budget."""

    error_code = "budget_exceeded"

    def __init__(self, agent_id: UUID, used: int, requested: int, budget: int) -> None:
        self.agent_id = agent_id
        self.used = used
        self.requested = requested
        self.budget = budget
        super().__init__(
            f"agent {agent_id} budget exceeded: used={used} requested={requested} budget={budget}"
        )


class ContextBudget:
    """Reads token ledger totals without storing mutable counters in memory."""

    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    async def tokens_used_today(self, agent_id: UUID, session: AsyncSession | None = None) -> int:
        """Return UTC-day token total for an agent."""

        start = datetime.combine(datetime.now(timezone.utc).date(), time.min, tzinfo=timezone.utc)
        stmt = (
            select(
                func.coalesce(
                    func.sum(
                        TokenLedger.tokens_in
                        + TokenLedger.tokens_out
                        + TokenLedger.cache_write_tokens
                    ),
                    0,
                )
            )
            .where(TokenLedger.agent_id == agent_id)
            .where(TokenLedger.occurred_at >= start)
        )
        if session is not None:
            return int((await session.execute(stmt)).scalar_one())

        async with self._sessionmaker() as owned_session:
            return int((await owned_session.execute(stmt)).scalar_one())
