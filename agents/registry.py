"""Agent registry.

The registry intentionally starts as a static mapping. Import-based plugin
discovery is deferred until external agent packages exist.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any
from uuid import UUID

from mycelium.agents.base import BaseAgent
from mycelium.agents.builtin.coder import CoderAgent
from mycelium.agents.builtin.echo import EchoAgent
from mycelium.agents.builtin.fetcher import FetcherAgent
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
    "fetcher": FetcherAgent,
    "shadow_debugger": ShadowDebuggerAgent,
}


def register_agent_type(agent_type: str, cls: type[BaseAgent]) -> None:
    """Register an agent implementation class."""

    _REGISTRY[agent_type] = cls


def create_agent(row: Agent) -> BaseAgent:
    """Create an agent implementation from a DB row."""

    return create_agent_from_values(
        agent_id=row.id,
        name=row.name,
        agent_type=row.type,
        system_prompt=row.system_prompt,
        model=row.model,
        config=row.config_jsonb,
    )


def create_agent_from_values(
    *,
    agent_id: UUID,
    name: str,
    agent_type: str,
    system_prompt: str,
    model: str,
    config: dict[str, Any],
) -> BaseAgent:
    """Create an agent implementation from explicit config values."""

    cls = _REGISTRY.get(agent_type)
    if cls is None:
        raise ValueError(f"unknown agent type: {agent_type}")
    return cls(
        agent_id=agent_id,
        name=name,
        system_prompt=system_prompt,
        model=model,
        config=config,
    )
