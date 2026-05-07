from __future__ import annotations

from mycelium.core.scheduler import TaskSpec


def test_task_spec_defaults() -> None:
    spec = TaskSpec(payload={"message": "hello"})

    assert spec.estimated_tokens == 4000
    assert spec.parent_task_id is None
