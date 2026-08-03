# Mycelium - Current State

Last verified: 2026-08-01 against remote `main` at `8ad76fedb747e2efbeb6d3834445905a3c146ed0`.

## Product

- Public repository, Phase 1 scaffold, currently on hold.
- No production or homelab deployment is recorded; `deploy/ct-readme.md` explicitly defers it.
- Python, UI, and Docker-build workflows exist. Image publication is disabled by this migration while on hold.

## Delivery Policy

- `main` is the sole long-lived branch. GitHub protection currently requires strict `python` and `ui` checks, linear history, no force pushes, and no branch deletion.
- Beads is not initialized; do not run `bd init` until hook integration is planned.
- Migration branch: `chore/homelab-fb2-delivery-policy` (fallback identity).
- Delivery-controller automation is disabled because the project is on hold and has no exact-SHA deployment verification or proven runtime rollback.
- Static verification passes: policy, Ruff, mypy, 21 tests, UI lint/type/build; 3 environment-gated integration tests skip. `npm audit --omit=dev` reports existing high-severity advisories in Next.js, PostCSS, and Sharp; dependencies and generated lockfiles remain unchanged for a separate protected task.

## Preserved Unique State

- The primary checkout has unique dirty agent-instruction, generated snapshot, and soak-run artifacts. Do not clean, reset, stage, or reuse them here.
- Linked worktree `.claude/worktrees/adr-0007-oauth-impl` is clean on `worktree-adr-0007-oauth-impl` and contains five commits unique relative to remote `main`, including OAuth-first provider, verification harness, and three-tier memory work. Preserve the worktree and branch exactly.

## Next Agent: Pick Up Here

Review this policy-only migration without enabling automation or resuming the product. Before any later cleanup, prove containment with Git; the OAuth/memory branch is not contained and is not a cleanup candidate.
