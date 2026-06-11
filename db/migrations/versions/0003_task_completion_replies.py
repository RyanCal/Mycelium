"""Add task completion reply metadata.

Revision ID: 0003_task_completion_replies
Revises: 0002_agent_config_versions
Create Date: 2026-05-08
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "0003_task_completion_replies"
down_revision = "0002_agent_config_versions"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "tasks",
        sa.Column("reply_to_agent_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "tasks",
        sa.Column("completion_correlation_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_tasks_reply_to_agent_id_agents",
        "tasks",
        "agents",
        ["reply_to_agent_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_tasks_reply_to_agent", "tasks", ["reply_to_agent_id"])
    op.create_index(
        "ix_tasks_completion_correlation",
        "tasks",
        ["completion_correlation_id"],
    )


def downgrade() -> None:
    op.drop_index("ix_tasks_completion_correlation", table_name="tasks")
    op.drop_index("ix_tasks_reply_to_agent", table_name="tasks")
    op.drop_constraint("fk_tasks_reply_to_agent_id_agents", "tasks", type_="foreignkey")
    op.drop_column("tasks", "completion_correlation_id")
    op.drop_column("tasks", "reply_to_agent_id")
