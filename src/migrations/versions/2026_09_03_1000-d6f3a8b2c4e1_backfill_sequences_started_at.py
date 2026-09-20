"""realign sequences.started_at on the first detection's recorded_at

Revision ID: d6f3a8b2c4e1
Revises: c4e9f1a2b3d5
Create Date: 2026-09-03 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d6f3a8b2c4e1"
down_revision: Union[str, None] = "c4e9f1a2b3d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Sequences now start at the capture time (recorded_at) of their first detection rather
    # than at its insertion time. Realign existing rows in one DISTINCT ON pass over
    # detections (sequence_id is not indexed); sequences with no detection left are untouched.
    op.execute(
        """
        UPDATE sequences s
        SET started_at = d.recorded_at
        FROM (
            SELECT DISTINCT ON (sequence_id) sequence_id, recorded_at
            FROM detections
            WHERE sequence_id IS NOT NULL
            ORDER BY sequence_id, recorded_at, created_at, id
        ) d
        WHERE d.sequence_id = s.id AND s.started_at <> d.recorded_at
        """
    )


def downgrade() -> None:
    # Data-only migration: the previous started_at values are not recoverable.
    pass
