from __future__ import annotations

from typing import Any
from uuid import uuid4

import pytest

from mycelium.agents.builtin.researcher import ResearcherAgent
from mycelium.core.llm.provider import CompletionResult


class _FakeLLM:
    def __init__(self) -> None:
        self.model: str | None = None
        self.system: str | None = None
        self.messages: list[dict[str, Any]] | None = None

    async def complete(
        self,
        messages: list[dict[str, Any]],
        *,
        system: str,
        model: str | None = None,
    ) -> CompletionResult:
        self.messages = messages
        self.system = system
        self.model = model
        return CompletionResult(
            text="findings", model=model or "fallback", input_tokens=1, output_tokens=2
        )

    async def embed(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]


@pytest.mark.asyncio
async def test_builtin_llm_agent_uses_agent_model() -> None:
    llm = _FakeLLM()
    agent = ResearcherAgent(
        agent_id=uuid4(),
        name="researcher",
        system_prompt="system prompt",
        model="catalog-model",
        config={},
    )
    agent.llm = llm

    result = await agent.run_step({"prompt": "summarize this"})

    assert result.data == {"agent": "researcher", "response": "findings"}
    assert result.llm_calls[0].model == "catalog-model"
    assert llm.model == "catalog-model"
    assert llm.system == "system prompt"
    assert llm.messages is not None
