# Mycelium

Mycelium is a bootstrap scaffold for an Agentic Operating System: a persistent,
self-healing, multi-agent kernel for autonomous business workflows.

The mental model is OS-shaped: the LLM is compute, Postgres and Redis are memory
and disk, agents are processes, Redis Pub/Sub is the bus, and Docker containers
are per-agent sandboxes.

## Bootstrap Status

This repository is Phase 0 only. It contains the directory architecture, kernel
draft, message contract, database schema, Docker and CI scaffolding, and a
minimal dashboard shell. Phase 1 will make the daemon, worker, and echo-agent
flow runnable end to end.

## Quickstart

```bash
cd /home/dev/workspace/mycelium
cp .env.example .env
uv sync
docker compose up -d db redis
uv run alembic upgrade head
uv run python -m mycelium.db.seed
uv run python -m mycelium.core.daemon
```

In another terminal:

```bash
uv run arq mycelium.core.workers.arq_worker.WorkerSettings
```

The API health endpoint is available at `http://localhost:8000/health`.

## License

MIT.
