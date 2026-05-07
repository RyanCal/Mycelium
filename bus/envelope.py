"""Message envelope schema for the Mycelium bus."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class Envelope(BaseModel):
    """Unit of inter-agent communication.

    Payload is the extension point; envelope metadata is fixed so logs can be
    replayed and correlated across daemon restarts.
    """

    id: UUID = Field(default_factory=uuid4)
    schema_version: Literal[1] = 1
    from_agent: UUID | None = None
    to_agent: UUID | None = None
    channel: str
    message_type: Literal["request", "reply", "broadcast", "system", "stream_chunk"]
    ts: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    payload: dict[str, Any] = Field(default_factory=dict)
    reply_to: UUID | None = None
    correlation_id: UUID | None = None
    priority: int = Field(default=50, ge=0, le=100)
    ttl_seconds: int | None = Field(default=None, ge=1)

    def is_expired(self, *, now: datetime | None = None) -> bool:
        """Return whether this envelope is past its TTL."""

        if self.ttl_seconds is None:
            return False
        now = now or datetime.now(timezone.utc)
        return (now - self.ts).total_seconds() > self.ttl_seconds
