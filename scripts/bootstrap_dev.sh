#!/usr/bin/env bash
set -euo pipefail

cd "$(dirname "$0")/.."

docker compose up -d db redis
uv sync
uv run alembic upgrade head
uv run python -m mycelium.db.seed

echo "Mycelium dev database is migrated and seeded."
