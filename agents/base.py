"""Base agent contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from mycelium.agents.spec import AgentSpec
from mycelium.bus.publisher import BusPublisher
from mycelium.core.llm.provider import CompletionResult, LLMProvider
from mycelium.core.scheduler import TaskSpec


@dataclass(frozen=True)
class AgentResult:
    """Result returned by an agent step."""

    data: dict[str, Any]
    tokens_used: int = 0
    llm_calls: list[CompletionResult] = field(default_factory=list)


@dataclass(frozen=True)
class SubAgentRequest:
    """Request for the kernel to materialize a child agent and task."""

    spec: AgentSpec
    task: TaskSpec


class BaseAgent:
    """Base class for runnable agent implementations."""

    def __init__(
        self,
        *,
        agent_id: UUID,
        name: str,
        system_prompt: str,
        model: str,
        config: dict[str, Any],
    ) -> None:
        self.agent_id = agent_id
        self.name = name
        self.system_prompt = system_prompt
        self.model = model
        self.config = config
        self.llm: LLMProvider | None = None
        self.bus: BusPublisher | None = None
        self.sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def bind(
        self,
        *,
        llm: LLMProvider,
        bus: BusPublisher,
        sessionmaker: async_sessionmaker[AsyncSession],
    ) -> None:
        """Attach process-local services before a worker runs this agent."""

        self.llm = llm
        self.bus = bus
        self.sessionmaker = sessionmaker

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        """Run one task step. Subclasses implement domain behavior."""

        raise NotImplementedError
