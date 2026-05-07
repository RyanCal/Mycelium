"""Redis Pub/Sub subscriber utilities."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator, Iterable
from contextlib import suppress
from typing import Any

import redis.asyncio as aioredis

from mycelium.bus.envelope import Envelope


class BusSubscriber:
    """Convert Redis Pub/Sub messages into typed envelopes."""

    def __init__(self, redis: aioredis.Redis) -> None:
        self._redis = redis

    async def subscribe(
        self,
        channels: Iterable[str],
        *,
        stop: asyncio.Event | None = None,
        poll_timeout: float = 0.5,
    ) -> AsyncGenerator[Envelope, None]:
        """Yield envelopes from exact channels and wildcard patterns."""

        exact = [channel for channel in channels if "*" not in channel]
        patterns = [channel for channel in channels if "*" in channel]
        pubsub = self._redis.pubsub()
        if exact:
            await pubsub.subscribe(*exact)
        if patterns:
            await pubsub.psubscribe(*patterns)

        try:
            while stop is None or not stop.is_set():
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=poll_timeout,
                )
                if message is None:
                    continue
                envelope = self._parse(message)
                if envelope is None or envelope.is_expired():
                    continue
                yield envelope
        finally:
            with suppress(Exception):
                await pubsub.aclose()  # type: ignore[no-untyped-call]

    def _parse(self, message: dict[str, Any]) -> Envelope | None:
        if message.get("type") not in {"message", "pmessage"}:
            return None
        data = message.get("data")
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        if not isinstance(data, str):
            return None
        return Envelope.model_validate_json(data)
