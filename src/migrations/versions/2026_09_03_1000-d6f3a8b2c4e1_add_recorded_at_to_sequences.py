"""add recorded_at column to sequences and backfill from the first detection

Revision ID: d6f3a8b2c4e1
Revises: c4e9f1a2b3d5
Create Date: 2026-09-03 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d6f3a8b2c4e1"
down_revision: Union[str, None] = "c4e9f1a2b3d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add as nullable first so existing rows don't violate the NOT NULL constraint.
    op.add_column("sequences", sa.Column("recorded_at", sa.DateTime(), nullable=True))
    # Backfill from the detection that started the sequence (earliest created_at, the same
    # row started_at comes from). One DISTINCT ON pass over detections rather than a
    # correlated subquery per sequence: detections.sequence_id is not indexed.
    op.execute(
        """
        UPDATE sequences s
        SET recorded_at = d.recorded_at
        FROM (
            SELECT DISTINCT ON (sequence_id) sequence_id, recorded_at
            FROM detections
            WHERE sequence_id IS NOT NULL
            ORDER BY sequence_id, created_at, id
        ) d
        WHERE d.sequence_id = s.id
        """
    )
    # Sequences with no detection left fall back to started_at.
    op.execute("UPDATE sequences SET recorded_at = started_at WHERE recorded_at IS NULL")
    # Tighten to NOT NULL to match the SQLModel definition.
    op.alter_column("sequences", "recorded_at", nullable=False)


def downgrade() -> None:
    op.drop_column("sequences", "recorded_at")
