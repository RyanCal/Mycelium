"""Sandbox image builder placeholder."""

from __future__ import annotations


async def build_sandbox_image(*_: object, **__: object) -> str:
    """Return the configured sandbox image name until Docker build wiring exists."""

    return "mycelium/sandbox-base:dev"
