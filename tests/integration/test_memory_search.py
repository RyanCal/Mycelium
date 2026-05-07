from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="Phase 2 enables pgvector memory search")


def test_memory_search_placeholder() -> None:
    assert True
