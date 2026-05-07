"""Reviewer agent placeholder for Phase 2."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent


class ReviewerAgent(BaseAgent):
    """Future agent that reviews artifacts emitted on the bus."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return AgentResult(data={"planned": "reviewer", "payload": payload})
