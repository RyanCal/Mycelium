"""Redis publisher with write-through comms logging."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import uuid4

import redis.asyncio as aioredis
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from mycelium.bus.envelope import Envelope
from mycelium.db.models import CommsLog

logger = logging.getLogger(__name__)


class BusPublisher:
    """Publish envelopes with best-effort comms-log durability."""

    def __init__(
        self,
        redis: aioredis.Redis,
        *,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        self._redis = redis
        self._sessionmaker = sessionmaker

    async def publish(self, envelope: Envelope) -> Envelope:
        """Publish an envelope after stamping current UTC time.

        Redis delivery wins over durability during a transient DB failure, so
        subscribers do not hang waiting for a message the publisher could send.
        """

        stamped = envelope.model_copy(update={"ts": datetime.now(timezone.utc)})
        try:
            async with self._sessionmaker() as session:
                session.add(
                    CommsLog(
                        id=uuid4(),
                        envelope_id=stamped.id,
                        from_agent=stamped.from_agent,
                        to_agent=stamped.to_agent,
                        channel=stamped.channel,
                        message_type=stamped.message_type,
                        payload_jsonb=stamped.payload,
                        reply_to_envelope_id=stamped.reply_to,
                        created_at=stamped.ts,
                    )
                )
                await session.commit()
        except Exception:
            logger.warning("comms_log.write_failed", extra={"envelope_id": str(stamped.id)})
        await self._redis.publish(stamped.channel, stamped.model_dump_json())
        return stamped
