"""Add agent config versions and scoring seams.

Revision ID: 0002_agent_config_versions
Revises: 0001_initial
Create Date: 2026-05-07
"""

from __future__ import annotations

from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0002_agent_config_versions"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "agent_config_versions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("system_prompt", sa.Text(), nullable=False),
        sa.Column("model", sa.String(length=128), nullable=False),
        sa.Column(
            "config_jsonb",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=128), nullable=False),
        sa.Column("created_by", sa.String(length=64), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.Column(
            "updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False
        ),
        sa.UniqueConstraint("agent_id", "version", name="uq_agent_config_versions_agent_version"),
    )
    op.create_index(
        "ix_agent_config_versions_agent_created",
        "agent_config_versions",
        ["agent_id", "created_at"],
    )
    op.create_index(
        op.f("ix_agent_config_versions_agent_id"),
        "agent_config_versions",
        ["agent_id"],
    )

    op.add_column(
        "agents",
        sa.Column("current_version_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_agents_current_version_id_agent_config_versions",
        "agents",
        "agent_config_versions",
        ["current_version_id"],
        ["id"],
        ondelete="SET NULL",
    )
    _backfill_existing_agent_versions()

    op.add_column(
        "tasks",
        sa.Column("config_version_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_tasks_config_version_id_agent_config_versions",
        "tasks",
        "agent_config_versions",
        ["config_version_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_tasks_config_version_id"), "tasks", ["config_version_id"])

    op.alter_column(
        "runs",
        "experiment_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=True,
    )
    op.add_column("runs", sa.Column("source_task_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("runs", sa.Column("agent_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column(
        "runs", sa.Column("config_version_id", postgresql.UUID(as_uuid=True), nullable=True)
    )
    op.add_column(
        "runs",
        sa.Column("state", sa.String(length=32), server_default="queued", nullable=False),
    )
    op.add_column(
        "runs", sa.Column("result_jsonb", postgresql.JSONB(astext_type=sa.Text()), nullable=True)
    )
    op.add_column("runs", sa.Column("error_text", sa.Text(), nullable=True))
    op.add_column(
        "runs",
        sa.Column("tokens_used", sa.Integer(), server_default="0", nullable=False),
    )
    op.create_foreign_key(
        "fk_runs_source_task_id_tasks",
        "runs",
        "tasks",
        ["source_task_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_runs_agent_id_agents",
        "runs",
        "agents",
        ["agent_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_foreign_key(
        "fk_runs_config_version_id_agent_config_versions",
        "runs",
        "agent_config_versions",
        ["config_version_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(op.f("ix_runs_source_task_id"), "runs", ["source_task_id"])
    op.create_index(op.f("ix_runs_agent_id"), "runs", ["agent_id"])
    op.create_index(op.f("ix_runs_config_version_id"), "runs", ["config_version_id"])

    op.create_table(
        "task_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "task_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tasks.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "scorer_agent_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("agents.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("score_kind", sa.String(length=32), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
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
    op.create_index(op.f("ix_task_scores_task_id"), "task_scores", ["task_id"])
    op.create_index(op.f("ix_task_scores_scorer_agent_id"), "task_scores", ["scorer_agent_id"])
    op.create_index("ix_task_scores_task_kind", "task_scores", ["task_id", "score_kind"])


def downgrade() -> None:
    op.drop_index("ix_task_scores_task_kind", table_name="task_scores")
    op.drop_index(op.f("ix_task_scores_scorer_agent_id"), table_name="task_scores")
    op.drop_index(op.f("ix_task_scores_task_id"), table_name="task_scores")
    op.drop_table("task_scores")

    op.drop_index(op.f("ix_runs_config_version_id"), table_name="runs")
    op.drop_index(op.f("ix_runs_agent_id"), table_name="runs")
    op.drop_index(op.f("ix_runs_source_task_id"), table_name="runs")
    op.drop_constraint(
        "fk_runs_config_version_id_agent_config_versions",
        "runs",
        type_="foreignkey",
    )
    op.drop_constraint("fk_runs_agent_id_agents", "runs", type_="foreignkey")
    op.drop_constraint("fk_runs_source_task_id_tasks", "runs", type_="foreignkey")
    op.drop_column("runs", "tokens_used")
    op.drop_column("runs", "error_text")
    op.drop_column("runs", "result_jsonb")
    op.drop_column("runs", "state")
    op.drop_column("runs", "config_version_id")
    op.drop_column("runs", "agent_id")
    op.drop_column("runs", "source_task_id")
    op.execute("DELETE FROM runs WHERE experiment_id IS NULL")
    op.alter_column(
        "runs",
        "experiment_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )

    op.drop_index(op.f("ix_tasks_config_version_id"), table_name="tasks")
    op.drop_constraint(
        "fk_tasks_config_version_id_agent_config_versions",
        "tasks",
        type_="foreignkey",
    )
    op.drop_column("tasks", "config_version_id")

    op.drop_constraint(
        "fk_agents_current_version_id_agent_config_versions",
        "agents",
        type_="foreignkey",
    )
    op.drop_column("agents", "current_version_id")
    op.drop_index(op.f("ix_agent_config_versions_agent_id"), table_name="agent_config_versions")
    op.drop_index("ix_agent_config_versions_agent_created", table_name="agent_config_versions")
    op.drop_table("agent_config_versions")


def _backfill_existing_agent_versions() -> None:
    bind = op.get_bind()
    rows = (
        bind.execute(
            sa.text(
                "SELECT id, system_prompt, model, config_jsonb "
                "FROM agents WHERE current_version_id IS NULL"
            )
        )
        .mappings()
        .all()
    )
    if not rows:
        return

    version_rows = []
    updates = []
    for row in rows:
        version_id = uuid4()
        version_rows.append(
            {
                "id": version_id,
                "agent_id": row["id"],
                "version": 1,
                "system_prompt": row["system_prompt"],
                "model": row["model"],
                "config_jsonb": row["config_jsonb"],
                "reason": "registered",
                "created_by": "migration",
            }
        )
        updates.append({"agent_id": row["id"], "version_id": version_id})

    agent_config_versions = sa.table(
        "agent_config_versions",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("agent_id", postgresql.UUID(as_uuid=True)),
        sa.column("version", sa.Integer),
        sa.column("system_prompt", sa.Text),
        sa.column("model", sa.String),
        sa.column("config_jsonb", postgresql.JSONB),
        sa.column("reason", sa.String),
        sa.column("created_by", sa.String),
    )
    op.bulk_insert(agent_config_versions, version_rows)
    for update in updates:
        bind.execute(
            sa.text(
                "UPDATE agents SET current_version_id = :version_id WHERE id = :agent_id"
            ),
            update,
        )
