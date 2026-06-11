"""Request/reply correlation for agents."""

from __future__ import annotations

import asyncio
from collections.abc import Iterable
from contextlib import suppress
from uuid import UUID

from mycelium.bus.envelope import Envelope
from mycelium.bus.publisher import BusPublisher
from mycelium.bus.subscriber import BusSubscriber


class RequestTimeout(TimeoutError):
    """Raised when no matching reply envelope arrives before the deadline."""

    def __init__(self, correlation_id: UUID) -> None:
        super().__init__(f"timed out waiting for reply {correlation_id}")
        self.correlation_id = correlation_id


class ReplyTracker:
    """Resolve futures when envelopes arrive with matching correlation ids."""

    def __init__(self) -> None:
        self._waiters: dict[UUID, asyncio.Future[Envelope]] = {}

    def wait_for(self, correlation_id: UUID) -> asyncio.Future[Envelope]:
        """Return a future that resolves when a reply arrives."""

        existing = self._waiters.get(correlation_id)
        if existing is not None:
            return existing
        loop = asyncio.get_running_loop()
        future: asyncio.Future[Envelope] = loop.create_future()
        self._waiters[correlation_id] = future
        return future

    def cancel(self, correlation_id: UUID) -> bool:
        """Cancel and remove a pending waiter."""

        future = self._waiters.pop(correlation_id, None)
        if future is None:
            return False
        if not future.done():
            future.cancel()
        return True

    def resolve(self, envelope: Envelope) -> bool:
        """Resolve a matching waiter and return whether one existed."""

        if envelope.correlation_id is None:
            return False
        future = self._waiters.pop(envelope.correlation_id, None)
        if future is None:
            return False
        if not future.done():
            future.set_result(envelope)
        return True

    async def listen(
        self,
        subscriber: BusSubscriber,
        channels: Iterable[str],
        *,
        stop: asyncio.Event | None = None,
        ready: asyncio.Event | None = None,
    ) -> None:
        """Resolve replies from a subscriber until ``stop`` is set or cancelled."""

        async for envelope in subscriber.subscribe(channels, stop=stop, ready=ready):
            self.resolve(envelope)

    async def request(
        self,
        *,
        publisher: BusPublisher,
        subscriber: BusSubscriber,
        envelope: Envelope,
        reply_channels: Iterable[str],
        timeout: float = 30.0,
    ) -> Envelope:
        """Publish a request envelope and wait for its correlated reply."""

        correlation_id = envelope.correlation_id
        if correlation_id is None:
            from uuid import uuid4

            correlation_id = uuid4()
        request = envelope.model_copy(
            update={
                "message_type": "request",
                "correlation_id": correlation_id,
            }
        )
        future = self.wait_for(correlation_id)
        stop = asyncio.Event()
        ready = asyncio.Event()
        listener = asyncio.create_task(
            self.listen(subscriber, reply_channels, stop=stop, ready=ready),
            name=f"reply-tracker-{correlation_id}",
        )
        try:
            try:
                await asyncio.wait_for(ready.wait(), timeout=timeout)
            except TimeoutError as exc:
                raise RequestTimeout(correlation_id) from exc
            await publisher.publish(request)
            try:
                return await asyncio.wait_for(future, timeout=timeout)
            except TimeoutError as exc:
                raise RequestTimeout(correlation_id) from exc
        finally:
            self.cancel(correlation_id)
            stop.set()
            listener.cancel()
            with suppress(asyncio.CancelledError):
                await listener
