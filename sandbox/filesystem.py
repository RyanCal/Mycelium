"""Per-agent sandbox filesystem paths."""

from __future__ import annotations

from pathlib import Path
from uuid import UUID


def agent_volume_path(root: str | Path, agent_id: UUID | str) -> Path:
    """Return the host path for an agent's persistent volume."""

    return Path(root) / str(agent_id)
