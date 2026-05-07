"""Initial Mycelium schema.

Revision ID: 0001_initial
Revises:
Create Date: 2026-05-07
"""

from __future__ import annotations

import os

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    embed_dim = int(os.environ.get("EMBED_DIM", "1024"))
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    agent_status = sa.Enum(
        "idle",
        "busy",
        "paused",
        "errored",
        "terminated",
        name="agentstatus",
        native_enum=False,
        length=32,
    )
    task_state = sa.Enum(
        "queued",
        "dispatched",
        "running",
        "complete",
        "failed",
        "cancelled",
        name="taskstate",
        native_enum=False,
        length=32,
    )

    op.create_table(
        "agents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("type", sa.String(length=64), nullable=False),
        sa.Column("status", agent_status, nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column(
            "config_jsonb",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("sandbox_container_id", sa.String(length=255), nullable=True),
        sa.Column("token_budget_daily", sa.Integer(), nullable=True),
        sa.Column("tokens_used_today", sa.Integer(), nullable=False),
        sa.Column("last_heartbeat_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("name"),
    )
    op.create_index("ix_agents_status", "agents", ["status"])
    op.create_index("ix_agents_type", "agents", ["type"])

    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "parent_task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("priority", sa.Integer(), nullable=False),
        sa.Column("state", task_state, nullable=False),
        sa.Column("payload_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("result_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("error_text", sa.Text(), nullable=True),
        sa.Column("token_budget", sa.Integer(), nullable=False),
        sa.Column("tokens_used", sa.Integer(), nullable=False),
        sa.Column("arq_job_id", sa.String(length=255), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_tasks_agent_state", "tasks", ["agent_id", "state"])
    op.create_index("ix_tasks_scheduler_hot", "tasks", ["state", "priority", "created_at"])

    op.create_table(
        "comms_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("envelope_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("from_agent", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("to_agent", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("channel", sa.String(length=255), nullable=False),
        sa.Column("message_type", sa.String(length=32), nullable=False),
        sa.Column("payload_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("reply_to_envelope_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_comms_log_envelope_id", "comms_log", ["envelope_id"])
    op.create_index("ix_comms_channel_created", "comms_log", ["channel", "created_at"])
    op.create_index("ix_comms_from_created", "comms_log", ["from_agent", "created_at"])
    op.create_index("ix_comms_to_created", "comms_log", ["to_agent", "created_at"])

    op.create_table(
        "memory_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=True,
        ),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(embed_dim), nullable=False),
        sa.Column("source_type", sa.String(length=64), nullable=False),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "metadata_jsonb",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_memory_agent_source", "memory_chunks", ["agent_id", "source_type"])
    op.execute(
        "CREATE INDEX memory_chunks_embedding_hnsw_idx "
        "ON memory_chunks USING hnsw (embedding vector_cosine_ops) "
        "WITH (m = 16, ef_construction = 64)"
    )

    op.create_table(
        "experiments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column(
            "candidate_config_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=False
        ),
        sa.Column("state", sa.String(length=32), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_experiments_agent_id", "experiments", ["agent_id"])

    op.create_table(
        "runs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "experiment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("experiments.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("baseline_score", sa.Integer(), nullable=True),
        sa.Column("candidate_score", sa.Integer(), nullable=True),
        sa.Column(
            "metrics_jsonb",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_runs_experiment_id", "runs", ["experiment_id"])

    op.create_table(
        "token_ledger",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column("tokens_in", sa.Integer(), nullable=False),
        sa.Column("tokens_out", sa.Integer(), nullable=False),
        sa.Column("cache_read_tokens", sa.Integer(), nullable=False),
        sa.Column("cache_write_tokens", sa.Integer(), nullable=False),
        sa.Column("cost_micros", sa.Integer(), nullable=False),
        sa.Column(
            "occurred_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
    )
    op.create_index("ix_token_ledger_agent_id", "token_ledger", ["agent_id"])
    op.create_index("ix_token_ledger_task_id", "token_ledger", ["task_id"])
    op.create_index("ix_token_ledger_agent_time", "token_ledger", ["agent_id", "occurred_at"])


def downgrade() -> None:
    op.drop_index("ix_token_ledger_agent_time", table_name="token_ledger")
    op.drop_index("ix_token_ledger_task_id", table_name="token_ledger")
    op.drop_index("ix_token_ledger_agent_id", table_name="token_ledger")
    op.drop_table("token_ledger")
    op.drop_index("ix_runs_experiment_id", table_name="runs")
    op.drop_table("runs")
    op.drop_index("ix_experiments_agent_id", table_name="experiments")
    op.drop_table("experiments")
    op.execute("DROP INDEX IF EXISTS memory_chunks_embedding_hnsw_idx")
    op.drop_index("ix_memory_agent_source", table_name="memory_chunks")
    op.drop_table("memory_chunks")
    op.drop_index("ix_comms_to_created", table_name="comms_log")
    op.drop_index("ix_comms_from_created", table_name="comms_log")
    op.drop_index("ix_comms_channel_created", table_name="comms_log")
    op.drop_index("ix_comms_log_envelope_id", table_name="comms_log")
    op.drop_table("comms_log")
    op.drop_index("ix_tasks_scheduler_hot", table_name="tasks")
    op.drop_index("ix_tasks_agent_state", table_name="tasks")
    op.drop_table("tasks")
    op.drop_index("ix_agents_type", table_name="agents")
    op.drop_index("ix_agents_status", table_name="agents")
    op.drop_table("agents")
