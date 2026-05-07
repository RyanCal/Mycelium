"""Kernel exception hierarchy.

Domain exceptions carry machine-readable fields so API handlers and UI clients
can present specific remediation instead of flattening everything to text.
"""

from __future__ import annotations

from uuid import UUID


class KernelError(Exception):
    """Base class for expected Mycelium domain failures."""

    error_code = "kernel_error"


class AgentNotFound(KernelError):
    """Raised when a task targets an unknown agent."""

    error_code = "agent_not_found"

    def __init__(self, agent_id: UUID) -> None:
        self.agent_id = agent_id
        super().__init__(f"agent not found: {agent_id}")


class TaskNotFound(KernelError):
    """Raised when task lookup fails."""

    error_code = "task_not_found"

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"task not found: {task_id}")


class SandboxError(KernelError):
    """Raised for expected Docker sandbox failures."""

    error_code = "sandbox_error"
