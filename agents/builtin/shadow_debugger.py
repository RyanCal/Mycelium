"""Shadow debugger agent placeholder for Phase 3."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent


class ShadowDebuggerAgent(BaseAgent):
    """Future agent that proposes prompt/config experiments."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return AgentResult(data={"planned": "shadow_debugger", "payload": payload})
