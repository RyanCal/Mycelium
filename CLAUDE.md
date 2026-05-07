# Mycelium - Agent Instructions

## Mission

Mycelium is an Agentic Operating System kernel for autonomous business agents.
The system should be persistent, debuggable, self-healing, and safe enough to run
24/7 in a homelab before it is exposed publicly.

## Four Pillars

- Kernel: `core/` owns scheduling, lifecycle, budget checks, settings, logging,
  and the embedded FastAPI app.
- Agents: `agents/` owns the agent contract, specs, registry, builtins, and
  prompts. Agents contain intelligence; the kernel contains plumbing.
- Bus: `bus/` owns the Redis Pub/Sub envelope, channel names, publisher,
  subscriber, and request/reply correlation.
- Memory and sandbox: `memory/`, `db/`, and `sandbox/` own state persistence,
  semantic recall, and isolated execution.

## Directory Ownership

- `.github/workflows/`: CI, Docker image build, and UI build checks.
- `docs/`: architecture notes and ADRs. Keep security decisions explicit here.
- `core/kernel.py`: central orchestrator. Keep public methods narrow and async.
- `core/daemon.py`: process entry. It wires settings, logging, DB, Redis, Arq,
  kernel, FastAPI, and signal handlers in one event loop.
- `core/api/`: HTTP surface. Handlers call the kernel directly in this process.
- `core/workers/`: Arq worker entry points. Workers are separate processes and
  must stay stateless across jobs.
- `agents/`: agent-facing abstractions. Adding a new builtin should touch the
  registry and a focused implementation file.
- `bus/`: every inter-agent message must use `Envelope`; payload is flexible,
  envelope metadata is not.
- `db/models.py`: schema source of truth. Migrations live in `db/migrations/`.
- `memory/`: hot/warm/cold memory tiers. Phase 2 activates pgvector search.
- `sandbox/`: all Docker socket access must stay behind `SandboxManager`.
- `ui/`: Next.js dashboard. This is a work surface, not a marketing site.
- `scripts/`: local operator scripts. Destructive scripts must be visibly named.
- `deploy/`: future Proxmox/systemd deployment notes.

## Security Notes

The kernel eventually mounts `/var/run/docker.sock` so it can control per-agent
containers. Treat that as root-equivalent host access. Keep this risk documented
in `docs/sandbox-security.md`, keep sandbox defaults network-isolated, and do
not let arbitrary API callers execute sandbox commands. The bootstrap dashboard
is single-user and protected by `MYCELIUM_ADMIN_TOKEN`.

## Code Clarity

Use explicit names, small modules, and direct async control flow. Add comments or
docstrings when they explain why a boundary exists, what invariant can break, or
which tradeoff was chosen. Do not add clever abstractions until there are enough
cases to justify them.

## Deferred Work

- Cloudflare Tunnel and Access integration wait until public exposure.
- Proxmox CT deployment docs wait until this leaves the dev box.
- OpenTelemetry wiring is deferred, but logging should keep clean seams.
- Multi-user auth is deferred; this is a single-user homelab service now.
