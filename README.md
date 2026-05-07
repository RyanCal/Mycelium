# Mycelium

Mycelium is a bootstrap scaffold for an Agentic Operating System: a persistent,
self-healing, multi-agent kernel for autonomous business workflows.

The mental model is OS-shaped: the LLM is compute, Postgres and Redis are memory
and disk, agents are processes, Redis Pub/Sub is the bus, and Docker containers
are per-agent sandboxes.

GitHub repo: `Mycelium`. Python package import path: `mycelium.*`. Both forms
are used intentionally.

## What Works Today

| Feature | Status |
|---|---|
| Echo agent end-to-end | Phase 1 |
| Multi-agent peer review | Phase 2 planned |
| Vector memory search | Phase 2 planned |
| Sandbox Docker exec | Phase 2 planned |
| Self-improvement / experiments | Phase 3 planned |

## Bootstrap Status

This repository is in Phase 1. The Docker stack boots Postgres, Redis, the
kernel, the worker, and the dashboard; the canonical echo-agent flow runs end to
end through the API, queue, worker, and database. Phase 2 adds multi-agent peer
review, vector memory search, sandbox execution, and the live comms stream.

## Quickstart

```bash
cd /home/dev/workspace/mycelium
cp .env.example .env
uv sync
docker compose up -d --build
```

The API health endpoint is available at `http://localhost:8000/health`.

## Running The Echo Agent

The echo agent is the canonical Phase 1 demo. It registers an agent, dispatches a
task, waits for the worker to complete it, and verifies the persisted result.

```bash
cp .env.example .env
docker compose up -d --build
make smoke
open http://localhost:3000
```

## License

MIT.
