"""Translate kernel domain exceptions to HTTP responses."""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from mycelium.core.context_budget import BudgetExceeded
from mycelium.core.exceptions import AgentNotFound, KernelError, TaskNotFound


def install_exception_handlers(app: FastAPI) -> None:
    """Install JSON handlers for expected kernel errors."""

    @app.exception_handler(AgentNotFound)
    async def agent_not_found(_: Request, exc: AgentNotFound) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": exc.error_code, "agent_id": str(exc.agent_id)},
        )

    @app.exception_handler(TaskNotFound)
    async def task_not_found(_: Request, exc: TaskNotFound) -> JSONResponse:
        return JSONResponse(
            status_code=404,
            content={"error": exc.error_code, "task_id": str(exc.task_id)},
        )

    @app.exception_handler(BudgetExceeded)
    async def budget_exceeded(_: Request, exc: BudgetExceeded) -> JSONResponse:
        return JSONResponse(
            status_code=409,
            content={
                "error": exc.error_code,
                "agent_id": str(exc.agent_id),
                "used": exc.used,
                "requested": exc.requested,
                "budget": exc.budget,
            },
        )

    @app.exception_handler(KernelError)
    async def kernel_error(_: Request, exc: KernelError) -> JSONResponse:
        return JSONResponse(status_code=500, content={"error": exc.error_code, "detail": str(exc)})
