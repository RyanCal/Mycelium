"""Bootstrap smoke check.

Phase 0 only verifies the API health route. Phase 1 extends this script to
register an echo agent, dispatch a task, and assert the completed result.
"""

from __future__ import annotations

import asyncio
import os

import httpx


async def main() -> None:
    base_url = os.environ.get("MYCELIUM_API_BASE_URL", "http://localhost:8000")
    async with httpx.AsyncClient(base_url=base_url, timeout=10) as client:
        response = await client.get("/health")
        response.raise_for_status()
        payload = response.json()
        assert payload["app"] == "mycelium"
        print(f"ok health status={payload['status']} redis={payload['redis']}")


if __name__ == "__main__":
    asyncio.run(main())
