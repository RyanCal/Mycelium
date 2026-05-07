from __future__ import annotations

from datetime import datetime, timedelta, timezone
from uuid import uuid4

from mycelium.core.kernel import Kernel
from mycelium.core.scheduler import TaskSpec


def test_score_priority_clamps_without_kernel_init() -> None:
    kernel = object.__new__(Kernel)
    task = TaskSpec(payload={"message": "hello"})

    assert kernel._score_priority(-10, task) == 0
    assert kernel._score_priority(120, task) == 100


def test_score_priority_bumps_child_and_deadline_without_kernel_init() -> None:
    kernel = object.__new__(Kernel)
    task = TaskSpec(
        payload={"message": "hello"},
        parent_task_id=uuid4(),
        deadline=datetime.now(timezone.utc) + timedelta(minutes=10),
    )

    assert kernel._score_priority(50, task) > 50
