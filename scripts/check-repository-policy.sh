#!/usr/bin/env bash
# Deterministic guard against active delivery-policy drift. Historical ADRs are read-only history.
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
errors=0

fail() {
  printf 'policy check: %s\n' "$1" >&2
  errors=$((errors + 1))
}

require_text() {
  grep -Fq -- "$2" "$ROOT/$1" || fail "$1 is missing required text: $2"
}

reject_pattern() {
  if grep -Eqi -- "$2" "$ROOT/$1"; then
    fail "$1 contains legacy policy: $3"
  fi
}

policy_files=(
  AGENTS.md CLAUDE.md PRODUCT.md CONTRIBUTING.md docs/STATE.md docs/SETUP.md docs/DECISIONS.md
  .github/pull_request_template.md .github/workflows/ci.yml
  .github/workflows/ui-build.yml .github/workflows/docker-build.yml .githooks/pre-push
)

for file in "${policy_files[@]}"; do
  [ -f "$ROOT/$file" ] || fail "missing required file: $file"
done

for file in "${policy_files[@]}"; do
  [ -f "$ROOT/$file" ] || continue
  reject_pattern "$file" '\bBD_ACTOR\b' 'wrong Beads actor variable'
  reject_pattern "$file" 'owner.?s explicit (ok|approval).*(production|merge)|production.*owner.?s explicit (ok|approval)' 'universal production approval'
  reject_pattern "$file" '(`dev`.*integration|integration.*`dev`|branches:[[:space:]]*\[main,[[:space:]]*dev\])' 'dev integration topology'
  reject_pattern "$file" 'git push --no-verify|git worktree remove --force|rm -rf.*worktree' 'unsafe bypass or cleanup'
  reject_pattern "$file" '(feat|fix|chore|docs)/<short>' 'branch without exact task identity'
done

[ ! -e "$ROOT/.github/workflows/verdict.yml" ] || fail 'comment-driven verdict workflow must not exist'
require_text AGENTS.md '`main` is the only long-lived branch'
require_text AGENTS.md 'Delivery-controller automation stays disabled'
require_text AGENTS.md 'PR comments are informational; controller state is authoritative'
require_text AGENTS.md 'Git proves they are merged/contained or empty'
require_text CONTRIBUTING.md '`<type>/<bead-id>-<slug>`'
require_text .github/pull_request_template.md 'Task: <exact bead ID>'
require_text .github/pull_request_template.md 'Author-Family:'
require_text .github/pull_request_template.md 'Exact-Head-Review:'
require_text .github/pull_request_template.md 'PR comments are informational'
require_text .github/workflows/ci.yml 'branches: [main]'
require_text .github/workflows/ci.yml 'bash scripts/check-repository-policy.sh'
require_text .github/workflows/ui-build.yml 'branches: [main]'
require_text .github/workflows/ui-build.yml 'npm ci'
require_text .github/workflows/docker-build.yml 'if: ${{ false }}'
require_text docs/STATE.md 'Delivery-controller automation is disabled'
require_text docs/SETUP.md '## Deployment Verification'
require_text docs/SETUP.md 'There is no deployed release or proven one-command runtime rollback.'

(cd "$ROOT" && python3 -c 'import pathlib, tomllib; tomllib.loads(pathlib.Path("pyproject.toml").read_text()); tomllib.loads(pathlib.Path("agents/catalog.toml").read_text())') || fail 'TOML validation failed'

if [ "$errors" -ne 0 ]; then
  printf 'repository policy check failed with %d error(s)\n' "$errors" >&2
  exit 1
fi

echo 'repository policy check passed'
