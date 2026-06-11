from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Iterable
from typing import Any, cast

import pytest

from mycelium.bus.envelope import Envelope
from mycelium.bus.reply_tracker import ReplyTracker, RequestTimeout


class _FakePublisher:
    def __init__(self) -> None:
        self.published: Envelope | None = None

    async def publish(self, envelope: Envelope) -> Envelope:
        self.published = envelope
        return envelope


class _ReplyingSubscriber:
    def __init__(self, publisher: _FakePublisher) -> None:
        self._publisher = publisher

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
            from_agent=request.to_agent,
            to_agent=request.from_agent,
            channel=reply_channels[0],
            message_type="reply",
            correlation_id=request.correlation_id,
            payload={"ok": True},
        )
        if stop is not None:
            stop.set()


class _SilentSubscriber:
    async def subscribe(
        self,
        channels: Iterable[str],
        *,
        stop: asyncio.Event | None = None,
        ready: asyncio.Event | None = None,
        poll_timeout: float = 0.5,
    ) -> AsyncGenerator[Envelope, None]:
        del channels, poll_timeout
        if ready is not None:
            ready.set()
        while stop is None or not stop.is_set():
            await asyncio.sleep(0.001)
        if False:
            yield Envelope(channel="unused", message_type="reply")


@pytest.mark.asyncio
async def test_request_publishes_and_resolves_correlated_reply() -> None:
    publisher = _FakePublisher()
    tracker = ReplyTracker()

    reply = await tracker.request(
        publisher=cast(Any, publisher),
        subscriber=cast(Any, _ReplyingSubscriber(publisher)),
        envelope=Envelope(
            channel="kernel.commands",
            message_type="request",
            payload={"event": "example.requested"},
        ),
        reply_channels=["agent.parent.inbox"],
        timeout=1.0,
    )

    assert publisher.published is not None
    assert publisher.published.correlation_id == reply.correlation_id
    assert reply.payload == {"ok": True}


@pytest.mark.asyncio
async def test_request_timeout_removes_waiter() -> None:
    tracker = ReplyTracker()

    with pytest.raises(RequestTimeout):
        await tracker.request(
            publisher=cast(Any, _FakePublisher()),
            subscriber=cast(Any, _SilentSubscriber()),
            envelope=Envelope(
                channel="kernel.commands",
                message_type="request",
                payload={"event": "example.requested"},
            ),
            reply_channels=["agent.parent.inbox"],
            timeout=0.01,
        )

    assert tracker._waiters == {}
