"""Shadow debugger agent placeholder for Phase 3."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent
from mycelium.agents.builtin._llm_step import run_llm_step


class ShadowDebuggerAgent(BaseAgent):
    """Propose prompt/config experiments for a target agent."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return await run_llm_step(
            self,
            payload,
            role="shadow_debugger",
            instruction="Analyze the target behavior and propose a minimal config experiment.",
        )
