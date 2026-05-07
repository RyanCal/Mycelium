from __future__ import annotations

import time
from typing import Any, cast

import pytest

from mycelium.core.scheduler import Scheduler, TaskSpec


def test_task_spec_defaults() -> None:
    spec = TaskSpec(payload={"message": "hello"})

    assert spec.estimated_tokens == 4000
    assert spec.parent_task_id is None


class _CountResult:
    def scalar_one(self) -> int:
        return 1


class _FakeSession:
    async def __aenter__(self) -> _FakeSession:
        return self

    async def __aexit__(self, *_: object) -> None:
        return None

    async def execute(self, _: object) -> _CountResult:
        return _CountResult()


class _FakeSessionmaker:
    def __call__(self) -> _FakeSession:
        return _FakeSession()


@pytest.mark.asyncio
async def test_drain_returns_after_timeout() -> None:
    scheduler = object.__new__(Scheduler)
    scheduler._sessionmaker = cast(Any, _FakeSessionmaker())

    started = time.monotonic()
    await scheduler.drain(timeout=0.1)

    assert time.monotonic() - started < 0.3
