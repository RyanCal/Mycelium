from __future__ import annotations

from types import SimpleNamespace
from typing import Any, cast
from uuid import uuid4

from mycelium.core.workers.arq_worker import _completion_reply_envelope
from mycelium.db.models import TaskState


def test_completion_reply_envelope_targets_parent_inbox() -> None:
    parent_id = uuid4()
    child_id = uuid4()
    task_id = uuid4()
    correlation_id = uuid4()

    envelope = _completion_reply_envelope(
        cast(
            Any,
            SimpleNamespace(
                id=task_id,
                parent_task_id=None,
                reply_to_agent_id=parent_id,
                completion_correlation_id=correlation_id,
                state=TaskState.complete,
                result_jsonb={"ok": True},
                error_text=None,
            ),
        ),
        cast(Any, SimpleNamespace(id=child_id)),
    )

    assert envelope is not None
    assert envelope.channel == f"agent.{parent_id}.inbox"
    assert envelope.to_agent == parent_id
    assert envelope.from_agent == child_id
    assert envelope.correlation_id == correlation_id
    assert envelope.payload["event"] == "task.completed"
    assert envelope.payload["result"] == {"ok": True}


def test_completion_reply_envelope_skips_tasks_without_reply_metadata() -> None:
    envelope = _completion_reply_envelope(
        cast(
            Any,
            SimpleNamespace(
                reply_to_agent_id=None,
                completion_correlation_id=None,
            ),
        ),
        cast(Any, SimpleNamespace(id=uuid4())),
    )

    assert envelope is None
