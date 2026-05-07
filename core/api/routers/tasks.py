"""Task API routes."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Query

from mycelium.core.api.deps import get_kernel, require_admin_token
from mycelium.core.kernel import Kernel
from mycelium.db.models import TaskState

router = APIRouter(
    prefix="/tasks",
    tags=["tasks"],
    dependencies=[Depends(require_admin_token)],
)


@router.get("")
async def list_tasks(
    state: TaskState | None = Query(default=None),
    agent_id: UUID | None = Query(default=None),
    kernel: Kernel = Depends(get_kernel),
) -> list[dict[str, Any]]:
    """List tasks by optional state and agent."""

    return await kernel.list_tasks(state=state, agent_id=agent_id)


@router.get("/{task_id}")
async def get_task(task_id: UUID, kernel: Kernel = Depends(get_kernel)) -> dict[str, Any]:
    """Return one task."""

    return await kernel.get_task(task_id)
