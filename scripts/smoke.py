"""End-to-end smoke check for the Phase 1 echo flow."""

from __future__ import annotations

import asyncio
import os
from typing import Any

import httpx


async def main() -> None:
    """Register echo, dispatch a task, and wait for completion."""

    base_url = os.environ.get("MYCELIUM_API_BASE_URL", "http://localhost:8000")
    token = os.environ.get("MYCELIUM_ADMIN_TOKEN", "change-me")
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(base_url=base_url, headers=headers, timeout=30) as client:
        health = (await client.get("/health")).raise_for_status().json()
        print(f"ok health status={health['status']} redis={health['redis']}")

        spec: dict[str, Any] = {
            "name": "echo-test",
            "type": "echo",
            "system_prompt": "You echo your input.",
            "model": "claude-3-5-haiku-latest",
            "config": {},
            "token_budget_daily": None,
        }
        agent_response = await client.post("/api/v1/agents", json=spec)
        agent_response.raise_for_status()
        agent = agent_response.json()
        print(f"ok registered agent_id={agent['id']}")

        task_response = await client.post(
            f"/api/v1/agents/{agent['id']}/tasks",
            json={"payload": {"message": "hello mycelium"}, "priority": 60},
        )
        task_response.raise_for_status()
        task = task_response.json()
        print(f"ok dispatched task_id={task['id']}")

        for _ in range(60):
            task_detail_response = await client.get(f"/api/v1/tasks/{task['id']}")
            task_detail_response.raise_for_status()
            task_detail = task_detail_response.json()
            if task_detail["state"] == "complete":
                assert task_detail["result_jsonb"]["echo"] == "hello mycelium", task_detail
                print(f"ok task complete result={task_detail['result_jsonb']}")
                return
            if task_detail["state"] == "failed":
                raise AssertionError(f"task failed: {task_detail['error_text']}")
            await asyncio.sleep(0.5)

    raise AssertionError("task did not complete within 30s")


if __name__ == "__main__":
    asyncio.run(main())
