"""Provider protocols for LLM completions and embeddings."""

from __future__ import annotations

from typing import Any, Protocol


class LLMProvider(Protocol):
    """Minimal provider interface agents depend on."""

    async def complete(self, messages: list[dict[str, Any]], *, system: str) -> str:
        """Return a text completion for a chat-style prompt."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for text chunks."""
