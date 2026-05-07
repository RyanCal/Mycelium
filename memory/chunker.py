"""Text chunking utilities."""

from __future__ import annotations


def chunk_text(text: str, *, chunk_size: int = 2000, overlap: int = 200) -> list[str]:
    """Split text into overlapping character chunks.

    Bootstrap uses character windows; Phase 2 swaps this for token-aware chunks.
    """

    if chunk_size <= 0:
        raise ValueError("chunk_size must be positive")
    if overlap < 0 or overlap >= chunk_size:
        raise ValueError("overlap must be non-negative and smaller than chunk_size")
    chunks: list[str] = []
    start = 0
    while start < len(text):
        chunks.append(text[start : start + chunk_size])
        start += chunk_size - overlap
    return chunks
