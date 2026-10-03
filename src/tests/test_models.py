import pytest
from sqlmodel import SQLModel, text
from sqlmodel.ext.asyncio.session import AsyncSession

# Hot-path indexes, declared in two places that must not drift: the alembic migration (what
# production runs) and __table_args__ in app.models (what create_all gives a test database built
# without migrations). Column ORDER is pinned, not just the names: a B-tree on (a, b) sorts by a
# first and is useless for b alone, so a reordered index serves none of these queries while still
# looking like harmless tidying. It also propagates, since the next --autogenerate turns a
# models.py reorder into a migration that drops and recreates the real index the wrong way round.
# The flag is whether the index is partial. Postgres normalises predicate text, so the
# assertion is presence, not wording: enough to catch a dropped WHERE turning the queue's
# handful of due rows into an entry per sequence.
EXPECTED_INDEXES = {
    "detections": {
        "ix_detections_sequence_id_created_at": (["sequence_id", "created_at"], False),
        "ix_detections_bucket_key": (["bucket_key"], False),
    },
    "sequences": {
        "ix_sequences_camera_pose_last_seen": (["camera_id", "pose_id", "last_seen_at"], False),
        "ix_sequences_validation_due_at": (["validation_due_at"], True),
    },
}


@pytest.mark.parametrize(("table", "expected"), EXPECTED_INDEXES.items())
def test_hot_path_indexes_are_declared_on_the_models(table: str, expected: dict):
    """Guards the model side, which no database assertion can cover: the test database is
    migrated, so the indexes are there whether or not __table_args__ still declares them."""
    declared = {
        index.name: (
            [c.name for c in index.columns],
            index.dialect_options["postgresql"].get("where") is not None,
        )
        for index in SQLModel.metadata.tables[table].indexes
    }
    for name, spec in expected.items():
        assert name in declared, f"not declared on {table}: {name}"
        assert declared[name] == spec, f"{name} declared as {declared[name]}, expected {spec}"


@pytest.mark.asyncio
@pytest.mark.parametrize(("table", "expected"), EXPECTED_INDEXES.items())
async def test_hot_path_indexes_exist_in_the_database(async_session: AsyncSession, table: str, expected: dict):
    """Guards the migration side: a fresh database must end up with all of them, in order.

    Only non-tautological because the container runs `alembic upgrade head` before pytest.
    `async_session` calls create_all, so against an unmigrated database this would pass off the
    model declarations alone.
    """
    stmt = text(
        "SELECT c.relname, "
        "  (SELECT array_agg(a.attname ORDER BY k.ord) "
        "     FROM unnest(i.indkey) WITH ORDINALITY AS k(attnum, ord) "
        "     JOIN pg_attribute a ON a.attrelid = i.indrelid AND a.attnum = k.attnum), "
        "  i.indpred IS NOT NULL "
        "FROM pg_index i "
        "JOIN pg_class c ON c.oid = i.indexrelid "
        "JOIN pg_class t ON t.oid = i.indrelid "
        "WHERE t.relname = :table"
    ).bindparams(table=table)
    present = {row[0]: (list(row[1] or []), row[2]) for row in (await async_session.exec(stmt)).all()}
    for name, spec in expected.items():
        assert name in present, f"missing on {table}: {name}"
        assert present[name] == spec, f"{name} built as {present[name]}, expected {spec}"
