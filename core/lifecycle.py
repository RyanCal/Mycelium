"""Async signal handling for daemon shutdown and future hot reload."""

from __future__ import annotations

import asyncio
import signal
from contextlib import suppress

from mycelium.core.kernel import Kernel


def install_signal_handlers(kernel: Kernel) -> None:
    """Register POSIX signal handlers that schedule async kernel operations."""

    loop = asyncio.get_running_loop()
    with suppress(NotImplementedError):
        loop.add_signal_handler(
            signal.SIGTERM,
            lambda: asyncio.create_task(kernel.stop_daemon()),
        )
        loop.add_signal_handler(
            signal.SIGINT,
            lambda: asyncio.create_task(kernel.stop_daemon()),
        )
        loop.add_signal_handler(
            signal.SIGHUP,
            lambda: asyncio.create_task(_reload(kernel)),
        )


async def _reload(kernel: Kernel) -> None:
    """Placeholder for prompt/settings reload without process restart."""

    kernel.settings.__class__.model_rebuild()
