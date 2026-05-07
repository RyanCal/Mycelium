"""Async signal handling for daemon shutdown and future hot reload."""

from __future__ import annotations

import asyncio
import signal
from contextlib import suppress

import uvicorn

from mycelium.core.kernel import Kernel


def install_signal_handlers(kernel: Kernel, server: uvicorn.Server | None = None) -> None:
    """Register POSIX signal handlers that schedule async kernel operations."""

    loop = asyncio.get_running_loop()

    def request_shutdown() -> None:
        if server is not None:
            server.should_exit = True
        asyncio.create_task(kernel.stop_daemon())

    with suppress(NotImplementedError):
        loop.add_signal_handler(
            signal.SIGTERM,
            request_shutdown,
        )
        loop.add_signal_handler(
            signal.SIGINT,
            request_shutdown,
        )
        loop.add_signal_handler(
            signal.SIGHUP,
            lambda: asyncio.create_task(_reload(kernel)),
        )


async def _reload(kernel: Kernel) -> None:
    """Placeholder for prompt/settings reload without process restart."""

    kernel.settings.__class__.model_rebuild()
