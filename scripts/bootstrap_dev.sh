#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose up -d db redis
uv sync
DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://mycelium:mycelium@localhost:5433/mycelium}" \
REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}" \
uv run alembic upgrade head
DATABASE_URL="${DATABASE_URL:-postgresql+asyncpg://mycelium:mycelium@localhost:5433/mycelium}" \
REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}" \
uv run python -m mycelium.db.seed

echo "Mycelium dev database is migrated and seeded."
