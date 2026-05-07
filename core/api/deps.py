"""FastAPI dependencies shared by routers."""

from __future__ import annotations

from collections.abc import AsyncGenerator
from typing import cast

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from mycelium.core.kernel import Kernel

bearer_scheme = HTTPBearer(auto_error=False)


def get_kernel(request: Request) -> Kernel:
    """Return the kernel attached by ``create_app``."""

    return cast(Kernel, request.app.state.kernel)


async def get_db(kernel: Kernel = Depends(get_kernel)) -> AsyncGenerator[AsyncSession, None]:
    """Yield a short-lived DB session."""

    async with kernel.sessionmaker() as session:
        yield session


async def require_admin_token(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    kernel: Kernel = Depends(get_kernel),
) -> None:
    """Require the single-user homelab bearer token."""

    expected = kernel.settings.mycelium_admin_token.get_secret_value()
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="missing bearer token")
    if credentials.credentials != expected:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="invalid bearer token")
