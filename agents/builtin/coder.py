"""Coder agent placeholder for Phase 2."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent
from mycelium.agents.builtin._llm_step import run_llm_step


class CoderAgent(BaseAgent):
    """Draft implementation guidance using the configured LLM."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return await run_llm_step(
            self,
            payload,
            role="coder",
            instruction="Plan or write the requested code change. Call out files and tests.",
        )
