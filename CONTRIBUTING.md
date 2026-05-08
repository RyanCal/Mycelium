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

Use focused branches with one of these prefixes: `feat/<short>`,
`fix/<short>`, `chore/<short>`, or `docs/<short>`.

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

The protected `main` branch requires the Python and UI checks to pass. Solo
development does not require review approval, but CI must stay green.

Large architecture changes should add or update an ADR in `docs/adr/`.
