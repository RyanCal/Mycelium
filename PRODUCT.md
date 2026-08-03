# Mycelium - Product Vision

## Problem

Autonomous business agents need a persistent operating substrate for scheduling, communication, memory, isolation, observability, and recovery instead of one-off prompt chains.

## Audience

Initially the owner operating a single-user homelab. The public repository may help technical contributors, but an untrusted public runtime is not the current audience.

## North Star

A persistent, debuggable, self-healing agent kernel that can run continuously in the homelab while keeping agent work isolated, state recoverable, and consequential authority explicit.

## Non-Goals

- Multi-tenant or untrusted public operation before auth and sandbox hardening.
- Treating Docker isolation as a security boundary equivalent to a VM.
- Deploying or publishing while the project is on hold.
- Building marketing, billing, or broad end-user surfaces during kernel validation.

## Success Measures

- The canonical agent flow completes across API, queue, worker, and database.
- Failures are observable and recoverable without corrupting persistent state.
- Memory retrieval and sandbox execution respect their documented boundaries.
- A homelab deployment can be verified by exact release SHA and rolled back predictably before automation is enabled.
