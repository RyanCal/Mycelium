.PHONY: dev worker test lint type fmt smoke reset pre-commit

dev:
	docker compose up -d db redis
	DATABASE_URL="$${DATABASE_URL:-postgresql+asyncpg://mycelium:mycelium@localhost:5433/mycelium}" REDIS_URL="$${REDIS_URL:-redis://localhost:6379/0}" uv run python -m mycelium.core.daemon

worker:
	DATABASE_URL="$${DATABASE_URL:-postgresql+asyncpg://mycelium:mycelium@localhost:5433/mycelium}" REDIS_URL="$${REDIS_URL:-redis://localhost:6379/0}" uv run arq mycelium.core.workers.arq_worker.WorkerSettings

test:
	uv run pytest

lint:
	uv run ruff check .
	cd ui && npm run lint

type:
	uv run mypy .
	cd ui && npm run type-check

fmt:
	uv run ruff format .

smoke:
	uv run python scripts/smoke.py

reset:
	./scripts/reset_dev.sh

pre-commit:
	uvx pre-commit install
