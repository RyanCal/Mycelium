# Security Policy

## Reporting

Please report vulnerabilities through GitHub Security Advisories for
`RyanCal/Mycelium` when available. If that is not possible, open a private
communication channel with the maintainer before publishing details.

## Current Security Posture

Mycelium is a single-user homelab project. It is not hardened for multi-tenant
or untrusted public use.

The highest-risk design choice is Docker control: the kernel can mount
`/var/run/docker.sock` to manage per-agent containers. Docker socket access is
root-equivalent on the host. An attacker who controls an agent or an unauthenticated
sandbox execution path may be able to affect the host.

Current mitigations:

- API routes that mutate agent/task state require `MYCELIUM_ADMIN_TOKEN`.
- Sandbox defaults are network-isolated.
- Docker access is intended to stay behind `sandbox.manager.SandboxManager`.

Known gaps:

- No per-agent identity or per-agent auth yet.
- No multi-user dashboard auth yet.
- No formal sandbox escape hardening beyond Docker defaults.

Response is best effort; there is no formal SLA.
