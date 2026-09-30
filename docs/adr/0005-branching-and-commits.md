# ADR 0005: Branching And Commits

## Current delivery policy (30 September 2026)

Finished software merges immediately. CI and reviews are advisory. No earlier tier, protected-path rule or owner code review holds a merge. Record intent, affected behavior, actual verification or its absence, likely breaking points and exact recovery. Verify the changed running flow after delivery and repair or roll back failures. New spending, destructive live-data operations and unrelated scope retain separate authority. Read the current global contract and published base-branch instructions when working from an older branch. Policy and recovery: [homelab delivery runbook](https://github.com/RyanCal/homelab/blob/main/runbooks/merge-guard.md).

Older merge/check requirements below are historical and superseded. Existing product constraints and intentional project parks remain in effect.


Status: Accepted

## Context

Mycelium is moving from bootstrap commits to feature work where each slice should
be easy to review, validate, and roll back. The project is currently maintained
by a solo developer, so the process should require CI without adding review
ceremony that slows down small changes.

## Decision

Use PR-based development for every change. Branches use `feat/<short>`,
`fix/<short>`, `chore/<short>`, or `docs/<short>`. PR titles follow
Conventional Commits, and squash merge uses the PR title as the final commit
message on `main`.

Protect `main` with required status checks for the Python and UI workflows,
linear history, no force pushes, and no deletions. Required reviewers are not
enabled for solo development.

## Consequences

Each PR becomes one squash commit on `main`, which makes rollback a normal
`git revert <sha>` operation. Conventional Commit titles give the changelog a
clean source of truth. Direct pushes to `main` are no longer part of the normal
workflow.
