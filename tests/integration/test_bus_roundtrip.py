from __future__ import annotations

import asyncio
from typing import Any

import pytest

from mycelium.bus.envelope import Envelope
from mycelium.bus.subscriber import BusSubscriber


class _FakePubSub:
    def __init__(self, envelope: Envelope) -> None:
        self._envelope = envelope
        self._sent = False

    async def subscribe(self, *_: str) -> None:
        return None

    async def psubscribe(self, *_: str) -> None:
        return None

    async def get_message(
        self,
        *,
        ignore_subscribe_messages: bool,
        timeout: float,
    ) -> dict[str, Any] | None:
        await asyncio.sleep(0)
        if self._sent:
            return None
        self._sent = True
        return {"type": "message", "data": self._envelope.model_dump_json()}

    async def aclose(self) -> None:
        return None


class _FakeRedis:
    def __init__(self, envelope: Envelope) -> None:
        self._envelope = envelope

    def pubsub(self) -> _FakePubSub:
        return _FakePubSub(self._envelope)


@pytest.mark.asyncio
async def test_subscriber_yields_message_then_exits_on_stop() -> None:
    envelope = Envelope(
        channel="kernel.events",
        message_type="system",
        payload={"event": "test"},
    )
    stop = asyncio.Event()
    subscriber = BusSubscriber(_FakeRedis(envelope))  # type: ignore[arg-type]

    received: list[Envelope] = []
    async for item in subscriber.subscribe(["kernel.events"], stop=stop, poll_timeout=0.01):
        received.append(item)
        stop.set()

    assert received[0].id == envelope.id
