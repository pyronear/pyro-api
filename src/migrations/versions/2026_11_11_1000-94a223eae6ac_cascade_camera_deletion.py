"""cascade camera deletion

Revision ID: 94a223eae6ac
Revises: f8b5c0d4e6a3
Create Date: 2026-11-11 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "94a223eae6ac"
down_revision: Union[str, None] = "f8b5c0d4e6a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (table, column, referred table): deleting a camera deletes its poses, sequences and detections,
# then the occlusion masks of those poses and the alert links of those sequences
_CASCADES = [
    ("poses", "camera_id", "cameras"),
    ("sequences", "camera_id", "cameras"),
    ("detections", "camera_id", "cameras"),
    ("occlusion_masks", "pose_id", "poses"),
    ("alerts_sequences", "sequence_id", "sequences"),
]


def _recreate_foreign_keys(ondelete: Union[str, None]) -> None:
    for table, column, referred in _CASCADES:
        # Default PostgreSQL name, as created by the initial migration
        name = f"{table}_{column}_fkey"
        op.drop_constraint(name, table, type_="foreignkey")
        op.create_foreign_key(name, table, referred, [column], ["id"], ondelete=ondelete)


def upgrade() -> None:
    _recreate_foreign_keys("CASCADE")


def downgrade() -> None:
    _recreate_foreign_keys(None)
