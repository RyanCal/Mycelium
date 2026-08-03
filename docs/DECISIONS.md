# Mycelium - Active Local Decisions

## 2026-08-01 - Main-only delivery policy while on hold

**Decision:** Keep one long-lived `main` branch and use exact-task PRs. Once the product resumes, routine reversible work may progress autonomously with proportionate deterministic checks and exact-head review. Auth, private memory/data, migrations, destructive work, sandbox/Docker authority, secrets, public exposure, and workflow/deploy/controller changes stop for authorization after full review. Controller state, not comments, owns verdict authority; cleanup requires Git proof.

**Why:** The solo-builder workflow should avoid release queues, but Mycelium's Docker socket, persistent memory, and future public API cross trust boundaries. The project is also explicitly on hold, so normalized policy must not reactivate delivery.

**Alternatives considered:** Add a permanent `dev` branch (rejected as stale-release overhead); retain short branch names without task identity (rejected because they cannot bind worktree/PR/review state); enable observe automation now (rejected because there is no task database or deployed SHA); alter existing GitHub protection (unnecessary for this documentation migration).

**Automation state:** Disabled until the owner resumes the product, Beads/hook migration is complete, deployment is exact-SHA verifiable, and rollback is proven.

**Revisit if:** The project resumes, gains a team, or moves from single-user homelab assumptions to public or multi-tenant operation.

Historical ADR `docs/adr/0005-branching-and-commits.md` remains unchanged as decision history; this active decision supersedes only its short branch-name convention.
