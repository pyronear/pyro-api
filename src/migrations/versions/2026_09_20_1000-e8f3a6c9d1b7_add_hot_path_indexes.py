"""add hot-path indexes for sequence matching, latest-bbox and shared frame lookups

Revision ID: e8f3a6c9d1b7
Revises: d6f3a8b2c4e1
Create Date: 2026-09-20 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "e8f3a6c9d1b7"
down_revision: Union[str, None] = "d6f3a8b2c4e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (index name, table, columns). Kept in sync with the __table_args__ declarations in
# app.models, which is what puts these indexes in create_all-built test databases too.
INDEXES = (
    ("ix_sequences_camera_pose_last_seen", "sequences", ["camera_id", "pose_id", "last_seen_at"]),
    ("ix_detections_sequence_id_created_at", "detections", ["sequence_id", "created_at"]),
    ("ix_detections_bucket_key", "detections", ["bucket_key"]),
)


def upgrade() -> None:
    # (camera_id, pose_id, last_seen_at) backs the pose's recently-seen sequences, read on
    # every POST /detections during spatial matching.
    #
    # (sequence_id, created_at) has five consumers:
    #   - get_latest_with_bbox, once per candidate sequence per POST /detections
    #   - the player's sequence reads (endpoints/sequences.py)
    #   - the validation worker's frame fetch (services/validation.py)
    #   - the frame-count subquery in crud_sequence.py, on every completed validation job
    #   - the new-sequence path in endpoints/detections.py, `sequence_id IS NULL` plus a
    #     created_at cutoff. B-trees index NULLs, so that is a prefix-plus-range match.
    #
    # (bucket_key) backs the sibling-row lookup on DELETE /detections/{id} only: a rare admin
    # operation, paid for with index maintenance on the highest-write table.
    #
    # Plain CREATE INDEX, not CONCURRENTLY: the deploy stops the backend before migrating
    # (.github/workflows/push.yml), so nothing writes to detections while these build.
    for index_name, table_name, columns in INDEXES:
        op.create_index(index_name, table_name, columns, unique=False)


def downgrade() -> None:
    for index_name, table_name, _ in reversed(INDEXES):
        op.drop_index(index_name, table_name=table_name)
