# Sandbox Security

The kernel will eventually mount `/var/run/docker.sock` to manage per-agent
containers. Docker socket access is root-equivalent on the host, so all access
must stay behind `sandbox.manager.SandboxManager`.

Defaults are intentionally conservative:

- `network_mode=none`
- per-agent volumes under `/var/lib/mycelium/agents`
- CPU and memory limits from settings
- no arbitrary sandbox exec endpoint without admin authentication
