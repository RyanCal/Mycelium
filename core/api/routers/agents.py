"""Agent API routes."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from mycelium.agents.spec import AgentSpec
from mycelium.core.api.deps import get_kernel, require_admin_token
from mycelium.core.kernel import Kernel
from mycelium.core.scheduler import TaskSpec

router = APIRouter(
    prefix="/agents",
    tags=["agents"],
    dependencies=[Depends(require_admin_token)],
)


class TaskCreate(BaseModel):
    """Task creation payload accepted under an agent."""

    payload: dict[str, Any]
    priority: int = Field(default=50, ge=0, le=100)
    estimated_tokens: int = Field(default=4000, ge=0)
    parent_task_id: UUID | None = None


@router.post("")
async def create_agent(spec: AgentSpec, kernel: Kernel = Depends(get_kernel)) -> dict[str, Any]:
    """Register or update an agent by name."""

    agent_id = await kernel.register_agent(spec)
    return await kernel.get_agent(agent_id)


@router.get("")
async def list_agents(kernel: Kernel = Depends(get_kernel)) -> list[dict[str, Any]]:
    """List agents."""

    return await kernel.list_agents()


@router.get("/{agent_id}")
async def get_agent(agent_id: UUID, kernel: Kernel = Depends(get_kernel)) -> dict[str, Any]:
    """Return one agent."""

    return await kernel.get_agent(agent_id)


@router.post("/{agent_id}/tasks")
async def create_agent_task(
    agent_id: UUID,
    payload: TaskCreate,
    kernel: Kernel = Depends(get_kernel),
) -> dict[str, Any]:
    """Dispatch a task to one agent."""

    task_id = await kernel.dispatch_task(
        agent_id,
        TaskSpec(
            payload=payload.payload,
            estimated_tokens=payload.estimated_tokens,
            parent_task_id=payload.parent_task_id,
        ),
        priority=payload.priority,
    )
    return await kernel.get_task(task_id)
