"""FastAPI app factory for the embedded daemon API."""

from __future__ import annotations

import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager, suppress
from typing import cast

import redis.asyncio as aioredis
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import FastAPI

from mycelium.core.api.exceptions import install_exception_handlers
from mycelium.core.api.routers import agents, comms, health, memory, sandbox, tasks
from mycelium.core.kernel import Kernel
from mycelium.core.settings import get_settings
from mycelium.db.connection import get_engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Own a kernel lifecycle when the daemon did not inject one."""

    kernel_task: asyncio.Task[None] | None = None
    if not getattr(app.state, "kernel_managed_externally", False):
        kernel = await _build_kernel()
        app.state.kernel = kernel
        kernel_task = asyncio.create_task(kernel.start_daemon(), name="api.kernel")
    try:
        yield
    finally:
        state_kernel = cast(Kernel | None, getattr(app.state, "kernel", None))
        if state_kernel is not None and not getattr(app.state, "kernel_managed_externally", False):
            await state_kernel.stop_daemon()
        if kernel_task is not None:
            kernel_task.cancel()
            with suppress(asyncio.CancelledError):
                await kernel_task


async def _build_kernel() -> Kernel:
    """Build a standalone kernel for tests and direct ASGI serving."""

    settings = get_settings()
    engine = get_engine(settings.database_url)
    redis: aioredis.Redis = aioredis.from_url(  # type: ignore[no-untyped-call]
        settings.redis_url,
        decode_responses=True,
    )
    arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    return Kernel(settings=settings, engine=engine, redis=redis, arq_pool=arq_pool)


def create_app(kernel: Kernel | None = None) -> FastAPI:
    """Create an API app bound to a live Kernel instance."""

    app = FastAPI(title="Mycelium Kernel API", version="0.1.0", lifespan=lifespan)
    app.state.kernel_managed_externally = kernel is not None
    if kernel is not None:
        app.state.kernel = kernel
    install_exception_handlers(app)
    app.include_router(health.router)
    app.include_router(agents.router, prefix="/api/v1")
    app.include_router(tasks.router, prefix="/api/v1")
    app.include_router(comms.router, prefix="/api/v1")
    app.include_router(memory.router, prefix="/api/v1")
    app.include_router(sandbox.router, prefix="/api/v1")
    return app
