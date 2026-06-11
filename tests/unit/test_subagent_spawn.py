from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Iterable
from typing import Any, cast
from uuid import UUID, uuid4

import pytest

from mycelium.agents.base import AgentResult, BaseAgent
from mycelium.agents.spec import AgentSpec
from mycelium.bus.envelope import Envelope
from mycelium.core.kernel import Kernel
from mycelium.db.models import TaskState


class _ParentAgent(BaseAgent):
    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        return AgentResult(data=payload)


class _FakePublisher:
    def __init__(self) -> None:
        self.published: Envelope | None = None

    async def publish(self, envelope: Envelope) -> Envelope:
        self.published = envelope
        return envelope


class _CompletionSubscriber:
    def __init__(self, publisher: _FakePublisher, *, child_agent_id: UUID, task_id: UUID) -> None:
        self._publisher = publisher
        self._child_agent_id = child_agent_id
        self._task_id = task_id

    async def subscribe(
        self,
        channels: Iterable[str],
        *,
        stop: asyncio.Event | None = None,
        ready: asyncio.Event | None = None,
        poll_timeout: float = 0.5,
    ) -> AsyncGenerator[Envelope, None]:
        del poll_timeout
        if ready is not None:
            ready.set()
        reply_channels = list(channels)
        while self._publisher.published is None:
            await asyncio.sleep(0)
        request = self._publisher.published
        yield Envelope(
            from_agent=self._child_agent_id,
            to_agent=request.from_agent,
            channel=reply_channels[0],
            message_type="reply",
            correlation_id=request.correlation_id,
            payload={
                "event": "task.completed",
                "agent_id": str(self._child_agent_id),
                "task_id": str(self._task_id),
                "state": TaskState.complete.value,
                "result": {"done": True},
                "error": None,
            },
        )
        if stop is not None:
            stop.set()


@pytest.mark.asyncio
async def test_base_agent_spawn_subagent_publishes_kernel_request_and_waits() -> None:
    parent_id = uuid4()
    child_agent_id = uuid4()
    child_task_id = uuid4()
    publisher = _FakePublisher()
    agent = _ParentAgent(
        agent_id=parent_id,
        name="parent",
        system_prompt="",
        model="parent-model",
        config={},
    )
    agent.bus = cast(Any, publisher)
    agent.subscriber = cast(
        Any,
        _CompletionSubscriber(
            publisher,
            child_agent_id=child_agent_id,
            task_id=child_task_id,
        ),
    )

    completion = await agent.spawn_subagent(
        spec=AgentSpec(
            name="child",
            type="researcher",
            system_prompt="child prompt",
            model="catalog-model",
            config={},
            token_budget_daily=1000,
        ),
        task_payload={"prompt": "collect context"},
        priority=77,
        estimated_tokens=123,
        timeout=1.0,
    )

    assert publisher.published is not None
    assert publisher.published.channel == "kernel.commands"
    assert publisher.published.from_agent == parent_id
    assert publisher.published.priority == 77
    assert publisher.published.payload["event"] == "subagent.requested"
    assert publisher.published.payload["spec"]["model"] == "catalog-model"
    assert publisher.published.payload["task"]["payload"] == {"prompt": "collect context"}
    assert completion.agent_id == child_agent_id
    assert completion.task_id == child_task_id
    assert completion.result == {"done": True}


class _KernelHarness:
    def __init__(self) -> None:
        self.child_agent_id = uuid4()
        self.child_task_id = uuid4()
        self.task_payload: Any = None
        self.priority: int | None = None

    async def register_agent(self, spec: AgentSpec) -> UUID:
        self.spec = spec
        return self.child_agent_id

    async def dispatch_task(self, agent_id: UUID, task: Any, priority: int = 50) -> UUID:
        assert agent_id == self.child_agent_id
        self.task_payload = task
        self.priority = priority
        return self.child_task_id


@pytest.mark.asyncio
async def test_kernel_spawn_subagent_adds_completion_reply_metadata() -> None:
    parent_id = uuid4()
    correlation_id = uuid4()
    harness = _KernelHarness()

    child_agent_id, child_task_id = await Kernel._spawn_subagent(
        cast(Any, harness),
        Envelope(
            from_agent=parent_id,
            channel="kernel.commands",
            message_type="request",
            correlation_id=correlation_id,
            payload={
                "event": "subagent.requested",
                "spec": AgentSpec(name="child", type="echo").model_dump(mode="json"),
                "task": {"payload": {"message": "hello"}, "estimated_tokens": 10},
                "priority": 66,
            },
        ),
    )

    assert child_agent_id == harness.child_agent_id
    assert child_task_id == harness.child_task_id
    assert harness.priority == 66
    assert harness.task_payload.reply_to_agent_id == parent_id
    assert harness.task_payload.completion_correlation_id == correlation_id
