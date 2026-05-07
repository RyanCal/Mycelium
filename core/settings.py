"""Typed runtime settings for the kernel and API.

All environment parsing is centralized here so daemon, workers, migrations, and
scripts agree on connection strings and model defaults. Defaults are local-first
and safe for Docker Compose development.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Literal

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment or ``.env``."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "mycelium"
    environment: Literal["development", "test", "production"] = "development"
    log_level: str = "INFO"

    database_url: str = "postgresql+asyncpg://mycelium:mycelium@localhost:5432/mycelium"
    redis_url: str = "redis://localhost:6379/0"
    arq_queue_name: str = "mycelium:arq"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = False
    mycelium_admin_token: SecretStr = Field(default=SecretStr("change-me"))

    anthropic_api_key: SecretStr | None = None
    anthropic_model: str = "claude-3-5-sonnet-latest"
    anthropic_prompt_cache: bool = True

    voyage_api_key: SecretStr | None = None
    embeddings_provider: Literal["voyage", "local"] = "voyage"
    embeddings_model: str = "voyage-3-large"
    embed_dim: int = 1024

    sandbox_base_image: str = "mycelium/sandbox-base:dev"
    sandbox_network_mode: str = "none"
    sandbox_cpu_quota: int = 50000
    sandbox_mem_limit: str = "512m"
    agent_volume_root: str = "/var/lib/mycelium/agents"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings for process lifetime."""

    return Settings()
