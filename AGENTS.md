# Mycelium agent instructions

## Delivery policy (30 September 2026)

Merge finished work immediately. Trusted ready PRs squash without waiting for CI, review, file-path classification or owner approval. CI is advisory. Resolve conflicts in your own branch; mark finished drafts ready. Small changes may go directly to the long-lived branch.

Before ending the task, record intent, behavior changed, actual verification or its absence, likely breaking points and exact rollback/recovery commands in the PR and relevant existing docs. Keep current state and non-obvious decisions understandable to the next agent. Fix or roll back failures after delivery. Git revert does not undo live-data changes or exposed credentials; document their separate recovery. Runtime trading/research activation, spending and destructive live operations retain their own authority rules.

This owner decision supersedes older merge/check/review requirements below. Canonical policy and recovery: `RyanCal/homelab`, `runbooks/merge-guard.md` and `decisions/2026-09-30-immediate-merges-and-documented-recovery.md`. Neither local hooks nor nested instructions may restore a blanket merge gate.


## Automatic immediate merging

The metadata-only merge-now workflow uses the dedicated homelab-gate runner with the single verdict-gate label. It squashes the exact current head of ready trusted same-repository PRs without waiting for CI or reviews. It never checks out PR code, calls a model or reads deployment secrets. The base-branch .github/automerge-tier file is the kill switch: on enables automatic merging; off stops it. Drafts remain unfinished work; conflicts stay with the owning agent.

If the runner is offline, the owning agent merges directly with `gh pr merge NUMBER --repo RyanCal/Mycelium --squash --match-head-commit SHA`, substituting this repository name and the exact current head. Do not wait for a queued workflow or introduce required checks to arm GitHub's native auto-merge. Document recovery, verify the delivered behavior and repair or roll back a failure. This policy does not restart a parked product or authorize unrelated runtime operations.


## Delivery-policy recovery

The immediate-merge installation is commit 24895c29b235075f28217839586e530153d4b2cb. If the owner intentionally reverses that policy, pause automatic merging first with `gh workflow disable guard.yml --repo RyanCal/Mycelium`, then create a new revert commit with `git revert --no-edit 24895c29b235075f28217839586e530153d4b2cb` on a branch based on current main. Restore former settings selectively from homelab's `ops/merge-now/2026-09-30/Mycelium-approved-before.json`; preserve later changes. Never reset or force-push shared history. Removing this repository's dedicated merge runner is a separate infrastructure operation recorded in homelab's runner service documentation.

For ordinary software defects, revert the affected squash commit or repair the running behavior, record the observed outcome and verify recovery. A Git revert does not undo live data or exposed credentials.
