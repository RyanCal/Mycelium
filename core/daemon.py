"""Daemon entry point for the Mycelium kernel and embedded FastAPI app."""

from __future__ import annotations

import asyncio

import redis.asyncio as aioredis
import uvicorn
from arq import create_pool
from arq.connections import RedisSettings

from mycelium.core.api.app import create_app
from mycelium.core.kernel import Kernel
from mycelium.core.lifecycle import install_signal_handlers
from mycelium.core.logging import configure
from mycelium.core.settings import get_settings
from mycelium.db.connection import get_engine


async def run() -> None:
    """Run kernel loops and the API server in one event loop."""

    settings = get_settings()
    configure(settings.log_level)

    engine = get_engine(settings.database_url)
    redis: aioredis.Redis = aioredis.from_url(  # type: ignore[no-untyped-call]
        settings.redis_url,
        decode_responses=True,
    )
    arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    kernel = Kernel(settings=settings, engine=engine, redis=redis, arq_pool=arq_pool)
    app = create_app(kernel)

    server = uvicorn.Server(
        uvicorn.Config(
            app,
            host=settings.api_host,
            port=settings.api_port,
            reload=settings.api_reload,
            log_config=None,
        )
    )
    install_signal_handlers(kernel)
    await asyncio.gather(kernel.start_daemon(), server.serve())


def main() -> None:
    """Console script wrapper."""

    asyncio.run(run())


if __name__ == "__main__":
    main()
