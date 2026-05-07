"""Request/reply correlation for agents."""

from __future__ import annotations

import asyncio
from uuid import UUID

from mycelium.bus.envelope import Envelope


class ReplyTracker:
    """Resolve futures when envelopes arrive with matching correlation ids."""

    def __init__(self) -> None:
        self._waiters: dict[UUID, asyncio.Future[Envelope]] = {}

    def wait_for(self, correlation_id: UUID) -> asyncio.Future[Envelope]:
        """Return a future that resolves when a reply arrives."""

        loop = asyncio.get_running_loop()
        future: asyncio.Future[Envelope] = loop.create_future()
        self._waiters[correlation_id] = future
        return future

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
