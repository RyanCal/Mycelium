# Mycelium

## Current delivery policy (30 September 2026)

Finished software merges immediately. CI and reviews are advisory. No earlier tier, protected-path rule or owner code review holds a merge. Record intent, affected behavior, actual verification or its absence, likely breaking points and exact recovery. Verify the changed running flow after delivery and repair or roll back failures. New spending, destructive live-data operations and unrelated scope retain separate authority. Read the current global contract and published base-branch instructions when working from an older branch. Policy and recovery: [homelab delivery runbook](https://github.com/RyanCal/homelab/blob/main/runbooks/merge-guard.md).

Older merge/check requirements below are historical and superseded. Existing product constraints and intentional project parks remain in effect.


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
