"""add alert shares

Revision ID: f8b5c0d4e6a3
Revises: e7a4b9c3d5f2
Create Date: 2026-10-30 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "f8b5c0d4e6a3"
down_revision: Union[str, None] = "e7a4b9c3d5f2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "alert_shares",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("alert_id", sa.Integer(), nullable=False),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["alert_id"], ["alerts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_alert_shares_alert_id"), "alert_shares", ["alert_id"], unique=False)
    op.create_index(op.f("ix_alert_shares_token_hash"), "alert_shares", ["token_hash"], unique=True)


def downgrade() -> None:
    op.drop_index(op.f("ix_alert_shares_token_hash"), table_name="alert_shares")
    op.drop_index(op.f("ix_alert_shares_alert_id"), table_name="alert_shares")
    op.drop_table("alert_shares")
