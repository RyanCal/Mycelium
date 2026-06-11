"""Fetcher agent placeholder for controlled network egress."""

from __future__ import annotations

from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent


class FetcherAgent(BaseAgent):
    """A registered fetcher type; network policy enforcement lands in H4."""

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return AgentResult(data={"planned": "fetcher", "payload": payload})
