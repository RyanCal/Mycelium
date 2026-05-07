"""Health endpoints for compose, CI, and operators."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends

from mycelium.core.api.deps import get_kernel
from mycelium.core.kernel import Kernel

router = APIRouter(tags=["health"])


@router.get("/")
@router.get("/health")
async def health(kernel: Kernel = Depends(get_kernel)) -> dict[str, Any]:
    """Return daemon health and a small amount of operational state."""

    return await kernel.health()
