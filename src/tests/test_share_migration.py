"""Exercise the share subject migration against PostgreSQL, in a rolled-back schema."""

from pathlib import Path
from uuid import uuid4

import pytest
from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from sqlalchemy import Column, Connection, Integer, MetaData, Table, inspect, text
from sqlalchemy.schema import CreateSchema

from app.db import engine


def _exercise_share_migration(connection: Connection) -> None:
    config = Config()
    config.set_main_option("script_location", str(Path(__file__).resolve().parents[1] / "migrations"))
    scripts = ScriptDirectory.from_config(config)
    old = scripts.get_revision("f8b5c0d4e6a3")
    new = scripts.get_revision("a9c6d1e5f7b4")
    assert new.down_revision == old.revision
    assert scripts.get_heads() == [new.revision]

    metadata = MetaData()
    for name in ("users", "organizations", "alerts"):
        table = Table(name, metadata, Column("id", Integer, primary_key=True))
        table.create(connection)
        connection.execute(table.insert(), [{"id": 1}, {"id": 2}])

    with Operations.context(MigrationContext.configure(connection)):
        old.module.upgrade()
        connection.execute(
            text("""
            INSERT INTO alert_shares
                (id, alert_id, organization_id, created_by, token_hash, created_at, expires_at, revoked_at)
            VALUES
                (1, 1, 1, 1, repeat('a', 64), '2026-01-01', '2100-01-01', NULL),
                (2, 1, 1, NULL, repeat('b', 64), '2026-01-02', '2026-01-03', '2026-01-02'),
                (3, 2, 2, 2, repeat('c', 64), '2026-01-03', '2100-01-01', NULL)
        """)
        )
        before = connection.execute(text("SELECT * FROM alert_shares ORDER BY id")).mappings().all()
        new.module.upgrade()
        after = connection.execute(text("SELECT * FROM alert_shares ORDER BY id")).mappings().all()
        assert [dict(row) for row in after] == [
            {**row, "created_by": str(row["created_by"]) if row["created_by"] is not None else None} for row in before
        ]
        columns = {column["name"]: column for column in inspect(connection).get_columns("alert_shares")}
        assert str(columns["created_by"]["type"]) == "VARCHAR"
        assert columns["created_by"]["nullable"]
        assert {tuple(fk["constrained_columns"]) for fk in inspect(connection).get_foreign_keys("alert_shares")} == {
            ("alert_id",),
            ("organization_id",),
        }
        indexes = {index["name"]: index for index in inspect(connection).get_indexes("alert_shares")}
        assert indexes["ix_alert_shares_token_hash"]["unique"]
        assert indexes["ix_alert_shares_alert_id"]["column_names"] == ["alert_id"]

        subject = "aa6ec0f1-bbbb-426e-b4fb-414b1c114fd1"
        connection.execute(
            text("""
                INSERT INTO alert_shares
                    (id, alert_id, organization_id, created_by, token_hash, created_at, expires_at)
                VALUES (4, 1, 1, :subject, repeat('d', 64), '2026-01-04', '2100-01-01')
            """),
            {"subject": subject},
        )
        connection.execute(text("DELETE FROM users WHERE id = 1"))
        assert connection.execute(text("SELECT created_by FROM alert_shares WHERE id = 1")).scalar_one() == "1"

        # Downgrading keeps links, clears UUIDs and deleted users, and restores representable legacy IDs.
        new.module.downgrade()
        assert connection.execute(text("SELECT id, created_by FROM alert_shares ORDER BY id")).all() == [
            (1, None),
            (2, None),
            (3, 2),
            (4, None),
        ]
        assert any(
            fk["constrained_columns"] == ["created_by"] for fk in inspect(connection).get_foreign_keys("alert_shares")
        )
        new.module.upgrade()
        assert connection.execute(text("SELECT id, created_by FROM alert_shares ORDER BY id")).all() == [
            (1, None),
            (2, None),
            (3, "2"),
            (4, None),
        ]


@pytest.mark.asyncio
async def test_share_creator_subject_migration():
    async with engine.connect() as connection:
        transaction = await connection.begin()
        try:
            schema = f"test_share_migration_{uuid4().hex}"
            await connection.execute(CreateSchema(schema))
            await connection.execute(text("SELECT set_config('search_path', :schema, true)"), {"schema": schema})
            await connection.run_sync(_exercise_share_migration)
        finally:
            await transaction.rollback()
