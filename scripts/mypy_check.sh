#!/usr/bin/env bash
# Run mypy with import paths matching runtime (mycelium.*).
#
# Mypy derives the top-level package name from the checkout directory. In
# environments where the repo root is not named "mycelium" (for example a
# container workdir named "workspace"), plain `mypy .` mis-attributes modules as
# workspace.* while sources import mycelium.*, which produces false positives.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TMP="$(mktemp -d)"
cleanup() {
  rm -rf "${TMP}"
}
trap cleanup EXIT
ln -sfn "${ROOT}" "${TMP}/mycelium"
cd "${TMP}"
exec uv run --project "${ROOT}" mypy --config-file "${ROOT}/pyproject.toml" --explicit-package-bases mycelium
