"""add hot-path indexes for sequence matching and shared frame objects

Revision ID: e8f3a6c9d1b7
Revises: c5e2f7a8b1d0
Create Date: 2026-07-22 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8f3a6c9d1b7"
down_revision: Union[str, None] = "c5e2f7a8b1d0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Latest-real-bbox lookups (spatial matching, notifications): sequence_id equality
    # with a created_at DESC scan; FK columns are not indexed automatically.
    op.create_index("ix_detections_sequence_id_created_at", "detections", ["sequence_id", "created_at"])
    # Sibling-row check on detection deletion: multi-bbox siblings and continuity rows
    # share one frame object, so deletes look up rows by bucket_key.
    op.create_index("ix_detections_bucket_key", "detections", ["bucket_key"])
    # Per-frame lookups of a pose's recently-seen sequences (spatial matching and the
    # continuity window both filter on camera_id, pose_id, last_seen_at).
    op.create_index("ix_sequences_camera_pose_last_seen", "sequences", ["camera_id", "pose_id", "last_seen_at"])


def downgrade() -> None:
    op.drop_index("ix_sequences_camera_pose_last_seen", table_name="sequences")
    op.drop_index("ix_detections_bucket_key", table_name="detections")
    op.drop_index("ix_detections_sequence_id_created_at", table_name="detections")
