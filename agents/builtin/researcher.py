"""Researcher agent placeholder for Phase 2."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent
from mycelium.agents.builtin._llm_step import run_llm_step


class ResearcherAgent(BaseAgent):
    """Draft findings from a task payload using the configured LLM."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return await run_llm_step(
            self,
            payload,
            role="researcher",
            instruction="Research the task and return concise findings with cited assumptions.",
        )
