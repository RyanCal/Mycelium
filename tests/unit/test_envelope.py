from __future__ import annotations

from datetime import datetime, timedelta, timezone

from mycelium.bus.envelope import Envelope


def test_envelope_round_trips_json() -> None:
    envelope = Envelope(
        channel="kernel.events",
        message_type="system",
        payload={"event": "agent.registered", "name": "echo-default"},
    )

    decoded = Envelope.model_validate_json(envelope.model_dump_json())

    assert decoded.id == envelope.id
    assert decoded.payload["event"] == "agent.registered"


def test_envelope_ttl_expiration() -> None:
    envelope = Envelope(
        channel="kernel.events",
        message_type="system",
        ts=datetime.now(timezone.utc) - timedelta(seconds=10),
        ttl_seconds=1,
    )

    assert envelope.is_expired()
