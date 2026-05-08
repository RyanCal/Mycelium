# ADR 0004: Root-Mapped Layout

Status: Accepted

## Context

Mycelium keeps domain directories such as `agents`, `core`, `db`, `memory`, and
`sandbox` at the repository root. Python imports still use the `mycelium.*`
namespace through `setuptools` `package-dir` mappings in `pyproject.toml`.

A conventional `src/mycelium/...` layout would make package discovery familiar,
but it would push the OS-shaped project structure one level deeper. This project
uses the top-level directories as part of the architecture: agents are processes,
the bus is IPC, Postgres and Redis are memory, and sandboxes are execution
boundaries.

## Decision

Keep the root-mapped layout and maintain explicit package mappings for every
Python package in `pyproject.toml`. Tests keep `pythonpath = ["."]`, and
contributors should import through `mycelium.*` rather than relying on raw
top-level module names.

Tooling that cannot infer the package-dir mapping should be configured
explicitly. Ruff, for example, treats `mycelium` as a first-party import.

## Consequences

The repository remains easy to scan by subsystem, and the Python import path
stays stable for installed packages. The tradeoff is that adding a new package
requires updating `pyproject.toml` package mappings intentionally.
