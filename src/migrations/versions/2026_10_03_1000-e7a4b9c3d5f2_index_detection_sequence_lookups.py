"""index detection and sequence ingestion lookups

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


def upgrade() -> None:
    # Concurrent builds allow ingestion to continue while existing tables are indexed.
    with op.get_context().autocommit_block():
        # Keep this index unfiltered: generic prepared plans cannot infer the bbox predicate.
        op.create_index(
            "ix_detections_sequence_created_at",
            "detections",
            ["sequence_id", sa.text("created_at DESC")],
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_detections_unassigned_camera_pose_created_at",
            "detections",
            ["camera_id", "pose_id", "created_at"],
            postgresql_where=sa.text("sequence_id IS NULL"),
            postgresql_concurrently=True,
        )
        op.create_index(
            "ix_sequences_camera_pose_last_seen_at",
            "sequences",
            ["camera_id", "pose_id", sa.text("last_seen_at DESC")],
            postgresql_concurrently=True,
        )


def downgrade() -> None:
    with op.get_context().autocommit_block():
        op.drop_index("ix_sequences_camera_pose_last_seen_at", table_name="sequences", postgresql_concurrently=True)
        op.drop_index(
            "ix_detections_unassigned_camera_pose_created_at", table_name="detections", postgresql_concurrently=True
        )
        op.drop_index("ix_detections_sequence_created_at", table_name="detections", postgresql_concurrently=True)
