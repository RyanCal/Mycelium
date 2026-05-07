"""Pydantic schemas for agent registration."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from mycelium.agents.catalog import load_agent_catalog


def _default_echo_model() -> str:
    return load_agent_catalog().entries["echo"].default_model


def _default_echo_token_budget() -> int | None:
    return load_agent_catalog().entries["echo"].daily_token_budget


class AgentSpec(BaseModel):
    """Definition used to register or update an agent."""

    name: str = Field(min_length=1, max_length=128)
    type: str = Field(default="echo", min_length=1, max_length=64)
    system_prompt: str = ""
    model: str = Field(default_factory=_default_echo_model)
    config: dict[str, Any] = Field(default_factory=dict)
    token_budget_daily: int | None = Field(default_factory=_default_echo_token_budget, ge=0)
