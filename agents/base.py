"""Base agent contract."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from mycelium.agents.spec import AgentSpec
from mycelium.bus.envelope import Envelope
from mycelium.bus.publisher import BusPublisher
from mycelium.bus.reply_tracker import ReplyTracker
from mycelium.bus.subscriber import BusSubscriber
from mycelium.core.llm.provider import CompletionResult, LLMProvider
from mycelium.core.scheduler import TaskSpec


@dataclass(frozen=True)
class AgentResult:
    """Result returned by an agent step."""

    data: dict[str, Any]
    tokens_used: int = 0
    llm_calls: list[CompletionResult] = field(default_factory=list)
    self_score: float | None = None
    reviewer_score: float | None = None


@dataclass(frozen=True)
class SubAgentRequest:
    """Request for the kernel to materialize a child agent and task."""

    spec: AgentSpec
    task: TaskSpec


@dataclass(frozen=True)
class SubAgentCompletion:
    """Completion payload returned after a spawned child task finishes."""

    agent_id: UUID
    task_id: UUID
    state: str
    result: dict[str, Any] | None
    error: str | None
    envelope: Envelope


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
        self.subscriber: BusSubscriber | None = None
        self.sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def bind(
        self,
        *,
        llm: LLMProvider,
        bus: BusPublisher,
        sessionmaker: async_sessionmaker[AsyncSession],
        subscriber: BusSubscriber | None = None,
    ) -> None:
        """Attach process-local services before a worker runs this agent."""

        self.llm = llm
        self.bus = bus
        self.subscriber = subscriber
        self.sessionmaker = sessionmaker

    async def spawn_subagent(
        self,
        *,
        spec: AgentSpec,
        task_payload: dict[str, Any],
        priority: int = 60,
        estimated_tokens: int = 4000,
        parent_task_id: UUID | None = None,
        timeout: float = 30.0,
    ) -> SubAgentCompletion:
        """Ask the kernel to run a child agent task and wait for completion."""

        if self.bus is None or self.subscriber is None:
            raise RuntimeError("agent bus publisher and subscriber must be bound before spawning")

        correlation_id = uuid4()
        task = TaskSpec(
            payload=task_payload,
            estimated_tokens=estimated_tokens,
            parent_task_id=parent_task_id,
        )
        reply = await ReplyTracker().request(
            publisher=self.bus,
            subscriber=self.subscriber,
            envelope=Envelope(
                from_agent=self.agent_id,
                channel="kernel.commands",
                message_type="request",
                correlation_id=correlation_id,
                priority=priority,
                payload={
                    "event": "subagent.requested",
                    "spec": spec.model_dump(mode="json"),
                    "task": task.model_dump(mode="json"),
                    "priority": priority,
                },
            ),
            reply_channels=[self.inbox_channel],
            timeout=timeout,
        )
        return SubAgentCompletion(
            agent_id=UUID(reply.payload["agent_id"]),
            task_id=UUID(reply.payload["task_id"]),
            state=reply.payload["state"],
            result=reply.payload.get("result"),
            error=reply.payload.get("error"),
            envelope=reply,
        )

    @property
    def inbox_channel(self) -> str:
        """Return the private bus channel this agent receives replies on."""

        return f"agent.{self.agent_id}.inbox"

    async def run_step(self, payload: dict[str, Any]) -> AgentResult:
        """Run one task step. Subclasses implement domain behavior."""

        raise NotImplementedError
