import pytest
from sqlmodel import SQLModel, text
from sqlmodel.ext.asyncio.session import AsyncSession

# Hot-path indexes, declared in two places that must not drift: the alembic migration (what
# production runs) and __table_args__ in app.models (what create_all gives a test database built
# without migrations). Drift is invisible at runtime, it just makes one environment plan queries
# differently from the other, so both sides are pinned against this list.
EXPECTED_INDEXES = {
    "detections": {"ix_detections_sequence_id_created_at", "ix_detections_bucket_key"},
    "sequences": {"ix_sequences_camera_pose_last_seen"},
}


@pytest.mark.parametrize(("table", "expected"), EXPECTED_INDEXES.items())
def test_hot_path_indexes_are_declared_on_the_models(table: str, expected: set):
    """Guards the model side. A DB assertion cannot cover this: the test database is migrated,
    so the indexes are present whether or not __table_args__ still declares them."""
    declared = {index.name for index in SQLModel.metadata.tables[table].indexes}
    assert expected <= declared, f"not declared on {table}: {sorted(expected - declared)}"


@pytest.mark.asyncio
@pytest.mark.parametrize(("table", "expected"), EXPECTED_INDEXES.items())
async def test_hot_path_indexes_exist_in_the_database(async_session: AsyncSession, table: str, expected: set):
    """Guards the migration side: a fresh database must end up with all of them."""
    stmt = text("SELECT indexname FROM pg_indexes WHERE tablename = :table").bindparams(table=table)
    present = {row[0] for row in (await async_session.exec(stmt)).all()}
    assert expected <= present, f"missing on {table}: {sorted(expected - present)}"
