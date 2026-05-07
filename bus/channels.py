"""Channel naming helpers for Redis Pub/Sub."""

from __future__ import annotations

from uuid import UUID

KERNEL_EVENTS = "kernel.events"
KERNEL_COMMANDS = "kernel.commands"
AGENTS_BROADCAST = "agents.broadcast"
MEMORY_INVALIDATE = "memory.invalidate"


def agent_inbox(agent_id: UUID | str) -> str:
    """Direct messages to one agent."""

    return f"agent.{agent_id}.inbox"


def agent_outbox(agent_id: UUID | str) -> str:
    """Broadcasts emitted by one agent."""

    return f"agent.{agent_id}.outbox"


def sandbox_stdout(agent_id: UUID | str) -> str:
    """Streamed stdout/stderr from an agent sandbox."""

    return f"sandbox.{agent_id}.stdout"


def sandbox_results(agent_id: UUID | str) -> str:
    """Final result envelopes from an agent sandbox."""

    return f"sandbox.{agent_id}.results"


def experiment_events(exp_id: UUID | str) -> str:
    """Experiment lifecycle events."""

    return f"experiments.{exp_id}.events"
