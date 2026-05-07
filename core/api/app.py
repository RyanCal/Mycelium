"""FastAPI app factory for the embedded daemon API."""

from __future__ import annotations

from fastapi import FastAPI

from mycelium.core.api.exceptions import install_exception_handlers
from mycelium.core.api.routers import agents, comms, health, memory, sandbox, tasks
from mycelium.core.kernel import Kernel


def create_app(kernel: Kernel) -> FastAPI:
    """Create an API app bound to a live Kernel instance."""

    app = FastAPI(title="Mycelium Kernel API", version="0.1.0")
    app.state.kernel = kernel
    install_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(agents.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(comms.router, prefix="/api/v1")
    app.include_router(memory.router, prefix="/api/v1")
    app.include_router(sandbox.router, prefix="/api/v1")
    return app
