"""Async SQLAlchemy engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from mycelium.core.settings import get_settings

_engines: dict[str, AsyncEngine] = {}
_sessionmakers: dict[str, async_sessionmaker[AsyncSession]] = {}


def get_engine(database_url: str | None = None) -> AsyncEngine:
    """Return a shared async engine for the given URL."""

    url = database_url or get_settings().database_url
    if url not in _engines:
        _engines[url] = create_async_engine(url, echo=False, pool_size=5, max_overflow=2)
    return _engines[url]


def get_session(database_url: str | None = None) -> async_sessionmaker[AsyncSession]:
    """Return a shared async session factory."""

    url = database_url or get_settings().database_url
    if url not in _sessionmakers:
        _sessionmakers[url] = async_sessionmaker(
            get_engine(url),
            class_=AsyncSession,
            expire_on_commit=False,
        )
    return _sessionmakers[url]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a short-lived DB session."""

    async with get_session()() as session:
        yield session
