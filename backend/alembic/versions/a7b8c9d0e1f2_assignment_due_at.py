"""add due_at to assignments

Revision ID: a7b8c9d0e1f2
Revises: f1d2e3c4b5a6
Create Date: 2026-06-15

Необязательный срок сдачи задания (информативный + напоминание).
"""
from alembic import op
import sqlalchemy as sa

revision = "a7b8c9d0e1f2"
down_revision = "f1d2e3c4b5a6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("assignments", sa.Column("due_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    op.drop_column("assignments", "due_at")
