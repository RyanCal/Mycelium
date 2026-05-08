"""Shared LLM step helper for builtin agents."""

from __future__ import annotations

import json
from typing import Any

from mycelium.agents.base import AgentResult, BaseAgent


async def run_llm_step(
    agent: BaseAgent,
    payload: dict[str, Any],
    *,
    role: str,
    instruction: str,
) -> AgentResult:
    """Run a simple catalog-configured LLM turn for a builtin agent."""

    prompt = _payload_to_prompt(payload)
    if agent.llm is None:
        return AgentResult(data={"planned": role, "payload": payload})

    completion = await agent.llm.complete(
        [
            {
                "role": "user",
                "content": f"{instruction}\n\nTask payload:\n{prompt}",
            }
        ],
        system=agent.system_prompt,
        model=agent.model,
    )
    return AgentResult(
        data={
            "agent": role,
            "response": completion.text,
        },
        llm_calls=[completion],
    )


def _payload_to_prompt(payload: dict[str, Any]) -> str:
    for key in ("prompt", "message", "task", "content"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value
    return json.dumps(payload, sort_keys=True, default=str)
