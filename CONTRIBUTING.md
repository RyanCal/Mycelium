# Contributing

## Development Setup

```bash
cp .env.example .env
./scripts/bootstrap_dev.sh
```

Run the daemon and worker in separate terminals:

```bash
uv run python -m mycelium.core.daemon
uv run arq mycelium.core.workers.arq_worker.WorkerSettings
```

Run the UI:

```bash
cd ui
npm install
npm run dev
```

## Branches And Pull Requests

Claim an exact task before writing and use `<type>/<bead-id>-<slug>`. Beads is not initialized
yet, so do not start new implementation work until task tracking and its hooks are migrated.
`chore/homelab-fb2-delivery-policy` is the one policy-migration exception.

Open a PR for every change and avoid direct pushes to `main`. PR titles should
follow Conventional Commits, such as `feat: add agent catalog` or
`fix: drain scheduler on shutdown`.

Squash merge with the PR title as the commit message. Each merged PR should map
to one commit on `main`, which keeps rollback simple: `git revert <sha>` undoes
one feature or fix without a surgical rebase.

Before opening a PR, run:

```bash
uv run ruff check .
uv run mypy .
uv run pytest
cd ui && npm run lint && npm run type-check && npm run build
```

The protected `main` branch requires the Python and UI checks to pass. Tiny localized work needs
deterministic checks and running smoke evidence. Substantial work needs independent exact-head
review. Protected auth/data/migration/sandbox/secret/workflow/deploy changes stop for owner or
specialist authorization after full review. CI must stay green; PR comments are informational and
do not authorize merge.

Large architecture changes should add or update an ADR in `docs/adr/`.
