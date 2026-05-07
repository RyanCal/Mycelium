"""Anthropic-first LLM provider."""

from __future__ import annotations

from typing import Any, cast

from anthropic import AsyncAnthropic

from mycelium.core.settings import Settings


class AnthropicProvider:
    """Thin adapter around Anthropic's SDK.

    Prompt caching is enabled by shaping stable system context as a cacheable
    block. The provider stays thin so cheaper models can be swapped later.
    """

    def __init__(self, settings: Settings) -> None:
        api_key = (
            settings.anthropic_api_key.get_secret_value() if settings.anthropic_api_key else None
        )
        self._client = AsyncAnthropic(api_key=api_key)
        self._model = settings.anthropic_model
        self._prompt_cache = settings.anthropic_prompt_cache

    async def complete(self, messages: list[dict[str, Any]], *, system: str) -> str:
        """Return a text completion."""

        system_param: str | list[dict[str, Any]]
        if self._prompt_cache:
            system_param = [
                {"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}
            ]
        else:
            system_param = system

        response = await self._client.messages.create(
            model=self._model,
            max_tokens=4096,
            system=cast(Any, system_param),
            messages=cast(Any, messages),
        )
        return "".join(
            str(getattr(block, "text", ""))
            for block in response.content
            if getattr(block, "type", None) == "text"
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Anthropic does not provide embeddings; callers should use VoyageProvider."""

        raise NotImplementedError("use VoyageEmbedProvider or LocalEmbedProvider for embeddings")
