"""Seed the default echo agent."""

from __future__ import annotations

import asyncio

import redis.asyncio as aioredis
from arq import create_pool
from arq.connections import RedisSettings

from mycelium.agents.spec import AgentSpec
from mycelium.core.kernel import Kernel
from mycelium.core.settings import get_settings
from mycelium.db.connection import get_engine


async def seed() -> None:
    """Register the bootstrap echo agent idempotently."""

    settings = get_settings()
    engine = get_engine(settings.database_url)
    redis: aioredis.Redis = aioredis.from_url(  # type: ignore[no-untyped-call]
        settings.redis_url,
        decode_responses=True,
    )
    arq_pool = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    kernel = Kernel(settings=settings, engine=engine, redis=redis, arq_pool=arq_pool)
    await kernel.register_agent(
        AgentSpec(
            name="echo-default",
            type="echo",
            system_prompt="Echo payloads for smoke tests.",
            model=settings.anthropic_model,
        )
    )
    await kernel.stop_daemon(drain_seconds=0)


def main() -> None:
    asyncio.run(seed())


if __name__ == "__main__":
    main()
