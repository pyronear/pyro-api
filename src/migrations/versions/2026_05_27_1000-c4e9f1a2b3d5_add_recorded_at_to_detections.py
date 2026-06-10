"""add recorded_at column to detections and backfill from created_at

Revision ID: c4e9f1a2b3d5
Revises: b3d8a9c1e2f4
Create Date: 2026-05-27 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c4e9f1a2b3d5"
down_revision: Union[str, None] = "b3d8a9c1e2f4"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add as nullable first so existing rows don't violate the NOT NULL constraint.
    op.add_column("detections", sa.Column("recorded_at", sa.DateTime(), nullable=True))
    # Backfill: legacy detections have no capture time, so fall back to the DB insertion time.
    op.execute("UPDATE detections SET recorded_at = created_at WHERE recorded_at IS NULL")
    # Tighten to NOT NULL to match the SQLModel definition.
    op.alter_column("detections", "recorded_at", nullable=False)


def downgrade() -> None:
    op.drop_column("detections", "recorded_at")
