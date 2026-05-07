"""Smoke-test agent used by the bootstrap and Phase 1 demo."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent


class EchoAgent(BaseAgent):
    """Return the incoming message so the queue path can be tested cheaply."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        message = payload.get("message", payload)
        return AgentResult(data={"echo": message}, tokens_used=0)
