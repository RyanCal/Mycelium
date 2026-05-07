"""Sandbox resource cap defaults."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ResourceCaps:
    """Docker limits applied to per-agent containers."""

    cpu_quota: int = 50000
    mem_limit: str = "512m"
    network_mode: str = "none"
