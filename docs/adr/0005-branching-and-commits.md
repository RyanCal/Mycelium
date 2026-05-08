# ADR 0005: Branching And Commits

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
