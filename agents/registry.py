"""Agent registry.

The registry intentionally starts as a static mapping. Import-based plugin
discovery is deferred until external agent packages exist.
"""

from __future__ import annotations

from collections.abc import Callable

from mycelium.agents.base import BaseAgent
from mycelium.agents.builtin.coder import CoderAgent
from mycelium.agents.builtin.echo import EchoAgent
from mycelium.agents.builtin.researcher import ResearcherAgent
from mycelium.agents.builtin.reviewer import ReviewerAgent
from mycelium.agents.builtin.shadow_debugger import ShadowDebuggerAgent
from mycelium.db.models import Agent

AgentFactory = Callable[..., BaseAgent]

_REGISTRY: dict[str, type[BaseAgent]] = {
    "echo": EchoAgent,
    "researcher": ResearcherAgent,
    "coder": CoderAgent,
    "reviewer": ReviewerAgent,
    "shadow_debugger": ShadowDebuggerAgent,
}


def register_agent_type(agent_type: str, cls: type[BaseAgent]) -> None:
    """Register an agent implementation class."""

    _REGISTRY[agent_type] = cls


def create_agent(row: Agent) -> BaseAgent:
    """Create an agent implementation from a DB row."""

    cls = _REGISTRY.get(row.type)
    if cls is None:
        raise ValueError(f"unknown agent type: {row.type}")
    return cls(
        agent_id=row.id,
        name=row.name,
        system_prompt=row.system_prompt,
        model=row.model,
        config=row.config_jsonb,
    )
