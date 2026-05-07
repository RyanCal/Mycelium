from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="Phase 1 enables Redis-backed bus roundtrip")


def test_bus_roundtrip_placeholder() -> None:
    assert True
