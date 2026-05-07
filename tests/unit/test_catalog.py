from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError

from mycelium.agents.catalog import AgentCatalogEntry, load_agent_catalog
from mycelium.agents.spec import AgentSpec


def test_load_agent_catalog_from_toml(tmp_path: Path) -> None:
    catalog_path = tmp_path / "catalog.toml"
    catalog_path.write_text(
        """
        [echo]
        description = "Echoes payloads."
        default_model = "claude-haiku"
        daily_token_budget = 10000
        prompt_file = "agents/prompts/system_base.md"
        network_access = false
        enabled = true
        """,
        encoding="utf-8",
    )

    catalog = load_agent_catalog(catalog_path)

    assert catalog.entries["echo"].enabled is True
    assert catalog.to_api()["echo"]["daily_token_budget"] == 10000
    load_agent_catalog.cache_clear()


def test_catalog_rejects_absolute_prompt_path() -> None:
    with pytest.raises(ValidationError):
        AgentCatalogEntry(
            description="Invalid",
            default_model="claude-haiku",
            daily_token_budget=10000,
            prompt_file="/tmp/prompt.md",
        )


def test_agent_spec_defaults_come_from_catalog() -> None:
    spec = AgentSpec(name="echo-default")
    echo = load_agent_catalog().entries["echo"]

    assert spec.model == echo.default_model
    assert spec.token_budget_daily == echo.daily_token_budget
