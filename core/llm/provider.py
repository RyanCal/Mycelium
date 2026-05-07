"""Provider protocols for LLM completions and embeddings."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class CompletionResult:
    """Text completion plus provider token usage."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        """Return token volume used by budget accounting."""

        return self.input_tokens + self.output_tokens + self.cache_write_tokens


class LLMProvider(Protocol):
    """Minimal provider interface agents depend on."""

    async def complete(self, messages: list[dict[str, Any]], *, system: str) -> CompletionResult:
        """Return a text completion for a chat-style prompt."""

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return embeddings for text chunks."""
