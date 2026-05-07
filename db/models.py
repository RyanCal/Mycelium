"""SQLAlchemy 2.0 schema for Mycelium."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
    text,
)
from sqlalchemy import (
    Enum as SQLEnum,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    """Declarative base used by Alembic."""


class TimestampMixin:
    """created_at / updated_at for mutable rows."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class AgentStatus(enum.StrEnum):
    idle = "idle"
    busy = "busy"
    paused = "paused"
    errored = "errored"
    terminated = "terminated"


class TaskState(enum.StrEnum):
    queued = "queued"
    dispatched = "dispatched"
    running = "running"
    complete = "complete"
    failed = "failed"
    cancelled = "cancelled"


class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    type: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    status: Mapped[AgentStatus] = mapped_column(
        SQLEnum(AgentStatus, native_enum=False, length=32),
        default=AgentStatus.idle,
        insert_default=AgentStatus.idle,
        nullable=False,
        index=True,
    )
    system_prompt: Mapped[str] = mapped_column(Text, nullable=False, default="", insert_default="")
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    config_jsonb: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )
    sandbox_container_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_budget_daily: Mapped[int | None] = mapped_column(Integer, nullable=True)
    tokens_used_today: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, insert_default=0
    )
    last_heartbeat_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    tasks: Mapped[list[Task]] = relationship(back_populates="agent", cascade="all, delete-orphan")


class Task(Base, TimestampMixin):
    __tablename__ = "tasks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
    )
    parent_task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="CASCADE"),
        nullable=True,
    )
    priority: Mapped[int] = mapped_column(Integer, nullable=False, default=50, insert_default=50)
    state: Mapped[TaskState] = mapped_column(
        SQLEnum(TaskState, native_enum=False, length=32),
        nullable=False,
        default=TaskState.queued,
        insert_default=TaskState.queued,
    )
    payload_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    result_jsonb: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    error_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    token_budget: Mapped[int] = mapped_column(Integer, nullable=False, default=0, insert_default=0)
    tokens_used: Mapped[int] = mapped_column(Integer, nullable=False, default=0, insert_default=0)
    arq_job_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    agent: Mapped[Agent] = relationship(back_populates="tasks")
    parent_task: Mapped[Task | None] = relationship(remote_side=[id])

    __table_args__ = (
        Index("ix_tasks_agent_state", "agent_id", "state"),
        Index("ix_tasks_scheduler_hot", "state", "priority", "created_at"),
    )


class CommsLog(Base):
    __tablename__ = "comms_log"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    envelope_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)
    from_agent: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    to_agent: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    channel: Mapped[str] = mapped_column(String(255), nullable=False)
    message_type: Mapped[str] = mapped_column(String(32), nullable=False)
    payload_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    reply_to_envelope_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (
        Index("ix_comms_channel_created", "channel", "created_at"),
        Index("ix_comms_from_created", "from_agent", "created_at"),
        Index("ix_comms_to_created", "to_agent", "created_at"),
    )


class MemoryChunk(Base, TimestampMixin):
    __tablename__ = "memory_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=True,
    )
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float]] = mapped_column(Vector(1024), nullable=False)
    source_type: Mapped[str] = mapped_column(String(64), nullable=False)
    source_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    metadata_jsonb: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )

    __table_args__ = (Index("ix_memory_agent_source", "agent_id", "source_type"),)


class Experiment(Base, TimestampMixin):
    __tablename__ = "experiments"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    hypothesis: Mapped[str] = mapped_column(Text, nullable=False)
    candidate_config_jsonb: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    state: Mapped[str] = mapped_column(
        String(32), nullable=False, default="draft", insert_default="draft"
    )


class Run(Base, TimestampMixin):
    __tablename__ = "runs"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("experiments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    baseline_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    candidate_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    metrics_jsonb: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'{}'::jsonb"),
    )


class TokenLedger(Base):
    __tablename__ = "token_ledger"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    agent_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    tokens_in: Mapped[int] = mapped_column(Integer, nullable=False, default=0, insert_default=0)
    tokens_out: Mapped[int] = mapped_column(Integer, nullable=False, default=0, insert_default=0)
    cache_read_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, insert_default=0
    )
    cache_write_tokens: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, insert_default=0
    )
    cost_micros: Mapped[int] = mapped_column(Integer, nullable=False, default=0, insert_default=0)
    occurred_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    __table_args__ = (Index("ix_token_ledger_agent_time", "agent_id", "occurred_at"),)
