"""Voyage embedding adapter."""

from __future__ import annotations

from voyageai import AsyncClient  # type: ignore[attr-defined]

from mycelium.core.settings import Settings


class VoyageEmbedProvider:
    """Embedding provider using Voyage, Anthropic's recommended partner."""

    def __init__(self, settings: Settings) -> None:
        api_key = settings.voyage_api_key.get_secret_value() if settings.voyage_api_key else None
        self._client = AsyncClient(api_key=api_key)
        self._model = settings.embeddings_model

    async def embed(self, texts: list[str]) -> list[list[float]]:
        """Return Voyage embeddings for text chunks."""

        response = await self._client.embed(texts, model=self._model)
        return [list(embedding) for embedding in response.embeddings]
