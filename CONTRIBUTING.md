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

Use focused branches such as `feat/echo-flow` or `fix/scheduler-drain`. Before
opening a PR, run:

```bash
uv run ruff check .
uv run mypy .
uv run pytest
cd ui && npm run lint && npm run type-check && npm run build
```

Large architecture changes should add or update an ADR in `docs/adr/`.
