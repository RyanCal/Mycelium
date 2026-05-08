from __future__ import annotations

import pytest

from mycelium.memory.chunker import chunk_text


def test_chunk_text_overlaps() -> None:
    chunks = chunk_text("abcdefghij", chunk_size=4, overlap=1)

    assert chunks == ["abcd", "defg", "ghij", "j"]


def test_chunk_text_rejects_bad_overlap() -> None:
    with pytest.raises(ValueError):
        chunk_text("abc", chunk_size=3, overlap=3)
