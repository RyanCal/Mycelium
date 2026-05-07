from __future__ import annotations

import pytest

pytestmark = pytest.mark.skip(reason="Phase 1 enables end-to-end register/dispatch flow")


def test_register_dispatch_flow_placeholder() -> None:
    assert True
