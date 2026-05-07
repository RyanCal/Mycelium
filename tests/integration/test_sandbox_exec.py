from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="Phase 2 enables Docker sandbox execution")


def test_sandbox_exec_placeholder() -> None:
    assert True
