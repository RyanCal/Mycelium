"""Docker-based per-agent sandbox manager skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID

from mycelium.sandbox.resource_caps import ResourceCaps


@dataclass
class SandboxManager:
    """Manage per-agent containers.

    The Docker socket is intentionally isolated behind this class so the security
    boundary is visible and auditable before Phase 2 enables real execution.
    """

    base_image: str
    volume_root: str
    caps: ResourceCaps = ResourceCaps()

    async def ensure_container(self, agent_id: UUID) -> str:
        """Return a container id for an agent, creating it in Phase 2."""

        raise NotImplementedError("sandbox containers are implemented in Phase 2")

    async def exec(self, agent_id: UUID, command: list[str]) -> dict[str, object]:
        """Execute a command inside an agent container in Phase 2."""

        raise NotImplementedError("sandbox exec is implemented in Phase 2")

    async def kill(self, agent_id: UUID) -> None:
        """Stop an agent container in Phase 2."""

        raise NotImplementedError("sandbox lifecycle is implemented in Phase 2")
