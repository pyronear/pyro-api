"""add hot-path indexes for sequence matching, latest-bbox and shared frame lookups

Revision ID: e8f3a6c9d1b7
Revises: c4e9f1a2b3d5
Create Date: 2026-07-30 10:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "e8f3a6c9d1b7"
down_revision: Union[str, None] = "c4e9f1a2b3d5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (index name, table, columns). Kept in sync with the __table_args__ declarations in
# app.models, which is what puts these indexes in create_all-built test databases too.
INDEXES = (
    ("ix_sequences_camera_pose_last_seen", "sequences", ["camera_id", "pose_id", "last_seen_at"]),
    ("ix_detections_sequence_id_created_at", "detections", ["sequence_id", "created_at"]),
    ("ix_detections_bucket_key", "detections", ["bucket_key"]),
)


def _drop_if_invalid(index_name: str, table_name: str) -> None:
    """Drop an index left INVALID by a cancelled CONCURRENTLY build.

    Without this the migration is not safely re-runnable: if_not_exists sees the leftover
    relation and skips creating it, the revision stamps, and the upgrade reports success while
    the planner ignores the invalid index, silently leaving these queries on sequential scans.

    The lookup joins pg_class by name rather than casting the name to regclass, since that cast
    raises when the relation does not exist yet (the common case) instead of returning no rows.
    """
    row = (
        op
        .get_bind()
        .execute(
            text(
                "SELECT idx.indisvalid FROM pg_index idx "
                "JOIN pg_class c ON c.oid = idx.indexrelid "
                "WHERE c.relname = :name"
            ),
            {"name": index_name},
        )
        .first()
    )
    if row is not None and not row[0]:
        op.drop_index(index_name, table_name=table_name, if_exists=True, postgresql_concurrently=True)


def upgrade() -> None:
    # Three query shapes on the detection hot path had no index backing them:
    #   - a pose's recently-seen sequences (camera_id, pose_id, last_seen_at), run on every
    #     POST /detections during spatial matching
    #   - the latest real bbox of a sequence (sequence_id, created_at), run once per candidate
    #     sequence per detection, and also the shape the player's sequence reads sort on
    #   - sibling rows sharing a frame object (bucket_key), on DELETE /detections/{id}
    #
    # detections is the highest-write table, so a plain CREATE INDEX would hold ACCESS EXCLUSIVE
    # against camera ingest for the whole build. CONCURRENTLY cannot run inside a transaction and
    # env.py wraps the migration run in one, hence the autocommit block.
    with op.get_context().autocommit_block():
        for index_name, table_name, columns in INDEXES:
            _drop_if_invalid(index_name, table_name)
            op.create_index(
                index_name,
                table_name,
                columns,
                unique=False,
                if_not_exists=True,
                postgresql_concurrently=True,
            )


def downgrade() -> None:
    # DROP INDEX CONCURRENTLY is likewise non-transactional.
    with op.get_context().autocommit_block():
        for index_name, table_name, _ in reversed(INDEXES):
            op.drop_index(index_name, table_name=table_name, if_exists=True, postgresql_concurrently=True)
