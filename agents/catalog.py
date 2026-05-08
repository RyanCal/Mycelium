"""Validated agent catalog loader."""

from __future__ import annotations

import tomllib
from functools import lru_cache
from pathlib import Path
from types import MappingProxyType
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

CATALOG_PATH = Path(__file__).with_name("catalog.toml")


class AgentCatalogEntry(BaseModel):
    """One agent type's operator-managed defaults."""

    model_config = ConfigDict(frozen=True)

    description: str
    default_model: str
    daily_token_budget: int = Field(ge=0)
    prompt_file: str
    network_access: bool = False
    enabled: bool = False
    cache_system_prompt: bool = False

    @field_validator("prompt_file")
    @classmethod
    def prompt_file_must_be_relative(cls, value: str) -> str:
        """Keep catalog prompt paths repository-relative."""

        if Path(value).is_absolute():
            raise ValueError("prompt_file must be repository-relative")
        return value


class AgentCatalog(BaseModel):
    """Frozen-ish view over all configured agent types."""

    model_config = ConfigDict(frozen=True)

    entries: dict[str, AgentCatalogEntry]

    @field_validator("entries")
    @classmethod
    def entries_must_not_be_empty(
        cls,
        value: dict[str, AgentCatalogEntry],
    ) -> dict[str, AgentCatalogEntry]:
        """Reject empty catalogs because the kernel needs at least echo."""

        if not value:
            raise ValueError("agent catalog must define at least one agent type")
        return value

    @property
    def frozen_entries(self) -> MappingProxyType[str, AgentCatalogEntry]:
        """Return a read-only mapping for in-process consumers."""

        return MappingProxyType(self.entries)

    def to_api(self) -> dict[str, dict[str, Any]]:
        """Return JSON-ready catalog data keyed by agent type."""

        return {
            agent_type: entry.model_dump()
            for agent_type, entry in sorted(self.entries.items(), key=lambda item: item[0])
        }


@lru_cache(maxsize=8)
def load_agent_catalog(path: Path | str | None = None) -> AgentCatalog:
    """Load and validate the TOML catalog."""

    catalog_path = Path(path) if path is not None else CATALOG_PATH
    raw = tomllib.loads(catalog_path.read_text(encoding="utf-8"))
    entries = {
        agent_type: AgentCatalogEntry.model_validate(config)
        for agent_type, config in raw.items()
    }
    return AgentCatalog(entries=entries)


def reload_agent_catalog() -> None:
    """Clear the catalog cache after an operator edits the TOML file."""

    load_agent_catalog.cache_clear()
