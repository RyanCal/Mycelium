# Memory Model

Mycelium uses three memory tiers:

- Hot: Redis keys for volatile working state.
- Warm: Postgres rows for task and communication history.
- Cold: pgvector-backed semantic chunks for durable recall.

Phase 2 activates cold-tier insertion and search. Phase 3 adds nightly hot to
warm summarization.
