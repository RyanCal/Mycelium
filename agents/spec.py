"""Pydantic schemas for agent registration."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class AgentSpec(BaseModel):
    """Definition used to register or update an agent."""

    name: str = Field(min_length=1, max_length=128)
    type: str = Field(default="echo", min_length=1, max_length=64)
    system_prompt: str = ""
    model: str = "claude-3-5-sonnet-latest"
    config: dict[str, Any] = Field(default_factory=dict)
    token_budget_daily: int | None = Field(default=None, ge=0)
