"""index detection and sequence lookups

Revision ID: e7a4b9c3d5f2
Revises: d6f3a8b2c4e1
Create Date: 2026-10-03 10:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "e7a4b9c3d5f2"
down_revision: Union[str, None] = "d6f3a8b2c4e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

INDEXES = (
    ("ix_detections_sequence_id_created_at", "detections", ["sequence_id", "created_at"], None),
    ("ix_sequences_camera_pose_last_seen", "sequences", ["camera_id", "pose_id", "last_seen_at"], None),
    ("ix_detections_bucket_key", "detections", ["bucket_key"], None),
    (
        "ix_detections_unassigned_camera_pose_created_at",
        "detections",
        ["camera_id", "pose_id", "created_at"],
        sa.text("sequence_id IS NULL"),
    ),
)


def upgrade() -> None:
    # Deployment stops the backend before migration; transactional builds avoid invalid indexes.
    for name, table, columns, predicate in INDEXES:
        op.create_index(name, table, columns, postgresql_where=predicate)


def downgrade() -> None:
    for name, table, _, _ in reversed(INDEXES):
        op.drop_index(name, table_name=table)
