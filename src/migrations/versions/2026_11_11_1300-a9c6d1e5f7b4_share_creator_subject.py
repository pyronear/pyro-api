"""Store share creators as token subjects, without requiring a local user.

Revision ID: a9c6d1e5f7b4
Revises: f8b5c0d4e6a3
Create Date: 2026-11-11 13:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "a9c6d1e5f7b4"
down_revision: Union[str, None] = "f8b5c0d4e6a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint("alert_shares_created_by_fkey", "alert_shares", type_="foreignkey")
    op.alter_column(
        "alert_shares",
        "created_by",
        existing_type=sa.Integer(),
        type_=sa.String(),
        existing_nullable=True,
        postgresql_using="created_by::text",
    )


def downgrade() -> None:
    # Keep every share, but clear subjects that the old users FK cannot represent.
    # Comparing as text also avoids casting UUIDs or oversized numeric subjects to int.
    op.execute("UPDATE alert_shares SET created_by = NULL WHERE created_by NOT IN (SELECT id::text FROM users)")
    op.alter_column(
        "alert_shares",
        "created_by",
        existing_type=sa.String(),
        type_=sa.Integer(),
        existing_nullable=True,
        postgresql_using="created_by::integer",
    )
    op.create_foreign_key(
        "alert_shares_created_by_fkey", "alert_shares", "users", ["created_by"], ["id"], ondelete="SET NULL"
    )
