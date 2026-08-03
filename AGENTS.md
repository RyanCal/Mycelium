# Mycelium - Agent Instructions

> Extends [`~/AGENTS.md`](/home/dev/AGENTS.md), which owns delivery defaults. Cold start: this file -> [`PRODUCT.md`](./PRODUCT.md) -> [`docs/STATE.md`](./docs/STATE.md).

## Mission

Mycelium is an Agentic Operating System kernel for persistent, debuggable, self-healing autonomous business agents. It must be safe in a single-user homelab before any public runtime exposure. Full vision: [`PRODUCT.md`](./PRODUCT.md).

## Current Posture

- The repository is public, but the product is on hold and has no deployed target.
- Do not resume feature development, deploy, publish an image, or expose a service without owner scope confirmation.
- `main` is protected by strict `python` and `ui` checks, linear history, no force pushes, and no deletion. Do not change GitHub settings as a side effect of code work.
- Beads is not initialized. Do not run `bd init` until hook and task-tracking migration is planned.

## Architecture Boundaries

- `core/`: scheduling, lifecycle, settings, logging, workers, and FastAPI.
- `agents/`: agent contracts, registry, builtins, catalog, and prompts.
- `bus/`: Redis Pub/Sub envelopes and request/reply correlation.
- `memory/` and `db/`: persistent and semantic state; migrations live in `db/migrations/`.
- `sandbox/`: Docker-backed execution. Docker socket access is root-equivalent.
- `ui/`: single-user Next.js work surface, not a public marketing site.

## Commands

```bash
uv sync --locked --dev
bash scripts/check-repository-policy.sh
uv run ruff check .
./scripts/mypy_check.sh
uv run pytest
cd ui && npm ci && npm run lint && npm run type-check && npm run build
```

Local running smoke: `docker compose up -d --build && make smoke`. Do not run deployment or publication checks while the project is on hold.

## Delivery

- **Topology:** `main` is the only long-lived branch. Work uses `<type>/<bead-id>-<slug>` and reaches `main` through an exact-task PR.
- **Task-tracking pause:** Delivery-controller automation stays disabled until Beads, hook integration, deployment verification, and rollback are established. `chore/homelab-fb2-delivery-policy` is the one migration exception.
- **Routine autonomy:** Once the product is resumed, routine reversible work may progress without owner permission after deterministic checks, running smoke evidence, and independent exact-head review when substantial.
- **Protected stop:** Auth/tokens, private memory/data, schema/migrations, destructive operations, sandbox or Docker access, secrets, public API exposure, `.github/**`, `deploy/**`, workflows, publication, and delivery/controller policy require full review and then owner or specialist authorization.
- **Review authority:** Tiny localized work uses deterministic checks and smoke evidence. Substantial work gets independent exact-head review. One automated fix and one delta review are allowed before one third-family arbiter or a genuine owner question. PR comments are informational; controller state is authoritative.
- **Cleanup:** Remove branches or worktrees only when Git proves they are merged/contained or empty. Preserve dirty, stashed, local-only, and otherwise unique state.

Exact setup, verification, and rollback constraints: [`docs/SETUP.md`](./docs/SETUP.md). Security posture: [`SECURITY.md`](./SECURITY.md).
