# Setup, Verification, And Rollback

## Local Setup

```bash
cp .env.example .env
uv sync --locked --dev
cd ui && npm ci
docker compose up -d --build
make smoke
```

Use development-only values locally. `MYCELIUM_ADMIN_TOKEN`, provider API keys, database credentials, and embedding credentials are secrets and must not be committed. Keep sandbox networking disabled unless an exact task requires reviewed egress.

## Static Validation

```bash
bash scripts/check-repository-policy.sh
uv run ruff check .
./scripts/mypy_check.sh
uv run pytest
cd ui && npm run lint && npm run type-check && npm run build
git diff --check
```

The tracked `.githooks/pre-push` is prepared but intentionally not activated while Beads is absent. Do not change shared `core.hooksPath` from a linked worktree.

## Deployment Verification

Deployment is deferred and image publication is disabled while the project is on hold. Before automation can be enabled, a protected deployment task must:

1. Record the target host/service and reviewed release SHA.
2. Apply reviewed database migrations separately and verify the live schema.
3. Bind a running health/version endpoint to the exact release SHA.
4. Exercise the API, queue/worker, persistence, memory, UI, and sandbox boundaries against the running target.
5. Prove the service and database recovery procedure without exposing secrets or private memory.

## Rollback

There is no deployed release or proven one-command runtime rollback. Keep delivery automation and image publication disabled until a versioned release can be restored with one command and any database recovery is separately tested. For a code-only PR that was not deployed, use `git revert <merge-sha>` through a new protected exact-task PR.
