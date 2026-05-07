"""Coder agent placeholder for Phase 2."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent


class CoderAgent(BaseAgent):
    """Future agent that changes code inside a sandbox."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return AgentResult(data={"planned": "coder", "payload": payload})
