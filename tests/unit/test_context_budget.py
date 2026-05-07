from __future__ import annotations

from uuid import uuid4

from mycelium.core.context_budget import BudgetExceeded


def test_budget_exceeded_message_contains_numbers() -> None:
    exc = BudgetExceeded(agent_id=uuid4(), used=90, requested=20, budget=100)

    assert exc.used == 90
    assert exc.requested == 20
    assert exc.budget == 100
