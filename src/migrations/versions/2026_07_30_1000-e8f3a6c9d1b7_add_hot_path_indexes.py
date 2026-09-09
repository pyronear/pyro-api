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


def _ensure_absent_or_replaceable(index_name: str, table_name: str, columns: list) -> None:
    """Clear the way for the create below, or fail loudly rather than silently skip.

    ``CREATE INDEX IF NOT EXISTS`` matches on the **name alone**: Postgres never compares the
    definition. So a same-named index over the wrong columns, or a leftover INVALID one from a
    cancelled CONCURRENTLY build, makes the create a no-op, the revision stamp, and the upgrade
    report success while the queries stay on sequential scans. Both are reachable on the manual
    pre-creation path, where a human types the column list.

    Anything else holding the name (a table, a view) is not ours to drop, so raise instead.
    """
    row = (
        op
        .get_bind()
        .execute(
            text(
                "SELECT c.relkind, i.indisvalid, t.relname, "
                "  (SELECT array_agg(a.attname ORDER BY k.ord) "
                "     FROM unnest(i.indkey) WITH ORDINALITY AS k(attnum, ord) "
                "     JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = k.attnum) AS cols "
                "FROM pg_class c "
                "JOIN pg_namespace n ON n.oid = c.relnamespace "
                "LEFT JOIN pg_index i ON i.indexrelid = c.oid "
                "LEFT JOIN pg_class t ON t.oid = i.indrelid "
                "WHERE c.relname = :name AND n.nspname = ANY (current_schemas(false))"
            ),
            {"name": index_name},
        )
        .first()
    )
    if row is None:
        return
    relkind, is_valid, owning_table, cols = row
    # pg_class.relkind is Postgres "char", which comes back as bytes over this driver.
    kind = relkind.decode() if isinstance(relkind, (bytes, bytearray)) else str(relkind)
    if kind != "i":
        raise RuntimeError(f"{index_name!r} already exists as relkind {kind!r}, not an index")
    if owning_table != table_name:
        raise RuntimeError(f"{index_name!r} already indexes {owning_table!r}, not {table_name!r}")
    if is_valid and list(cols or []) == list(columns):
        return
    op.drop_index(index_name, table_name=table_name, if_exists=True, postgresql_concurrently=True)


def upgrade() -> None:
    # Three query shapes on the detection hot path had no index backing them:
    #   - a pose's recently-seen sequences (camera_id, pose_id, last_seen_at), run on every
    #     POST /detections during spatial matching
    #   - the latest real bbox of a sequence (sequence_id, created_at), run once per candidate
    #     sequence per detection, and also the shape the player's sequence reads sort on
    #   - sibling rows sharing a frame object (bucket_key), on DELETE /detections/{id}
    #
    # detections is the highest-write table, so a plain CREATE INDEX holds SHARE against camera
    # ingest for the whole build (blocking writes, not reads). CONCURRENTLY cannot run inside a transaction and
    # env.py wraps the migration run in one, hence the autocommit block.
    with op.get_context().autocommit_block():
        for index_name, table_name, columns in INDEXES:
            _ensure_absent_or_replaceable(index_name, table_name, columns)
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
