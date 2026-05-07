"""Researcher agent placeholder for Phase 2."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent


class ResearcherAgent(BaseAgent):
    """Future agent that gathers and stores external findings."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return AgentResult(data={"planned": "researcher", "payload": payload})
