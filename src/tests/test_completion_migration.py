from importlib import import_module

import pytest
from alembic.migration import MigrationContext
from alembic.operations import Operations
from sqlalchemy import text

from app.db import engine


@pytest.mark.asyncio
async def test_completion_migration_preserves_verdicts_and_recovers_legacy_failures(monkeypatch):
    migration = import_module("migrations.versions.2026_11_06_1000-a9c2e5f7b1d3_separate_alert_completion_state")

    def migrate(connection):
        # A temporary table shadows the app table only on this connection. Exercise the
        # real PostgreSQL migration against all old states without touching fixture data.
        connection.execute(
            text("""
            CREATE TEMPORARY TABLE sequences (
                id integer PRIMARY KEY, is_validated boolean NOT NULL,
                validation_status varchar(32), validation_attempts integer NOT NULL,
                validation_due_at timestamp, validation_lease_until timestamp
            ) ON COMMIT DROP
        """)
        )
        connection.execute(
            text("""
            INSERT INTO sequences VALUES
                (1, false, NULL, 2, now(), NULL),
                (2, false, 'failed', 5, NULL, NULL),
                (3, false, 'window_exhausted', 0, NULL, NULL),
                (4, true, 'model', 2, now(), now()),
                (5, true, 'fail_open_unavailable', 0, NULL, NULL),
                (6, true, 'failed', 5, NULL, NULL),
                (7, true, NULL, 0, NULL, NULL)
        """)
        )
        monkeypatch.setattr(migration, "op", Operations(MigrationContext.configure(connection)))
        migration.upgrade()
        rows = connection.execute(
            text("""
            SELECT id, validation_status, validation_attempts, completion_status,
                   completion_attempts, validation_due_at IS NOT NULL, validation_lease_until IS NOT NULL
            FROM sequences ORDER BY id
        """)
        ).all()
        assert [tuple(row) for row in rows] == [
            (1, None, 2, None, 0, True, False),
            (2, "failed", 5, None, 0, False, False),
            (3, "window_exhausted", 0, None, 0, False, False),
            (4, "model", 0, "pending", 2, True, True),
            (5, "fail_open_unavailable", 0, "completed", 0, False, False),
            (6, None, 0, "failed", 5, False, False),
            (7, None, 0, "completed", 0, False, False),
        ]
        assert (
            connection.execute(text("SELECT completion_suppress_notifications FROM sequences")).scalars().all()
            == [False] * 7
        )
        # Old workers omit this new column when inserting; its server default is required.
        connection.execute(text("INSERT INTO sequences (id, is_validated, validation_attempts) VALUES (8, false, 0)"))
        assert (
            connection.execute(
                text("SELECT completion_suppress_notifications FROM sequences WHERE id = 8")
            ).scalar_one()
            is False
        )
        connection.execute(text("DELETE FROM sequences WHERE id = 8"))
        migration.downgrade()
        rows = connection.execute(
            text("""
            SELECT id, validation_status, validation_attempts FROM sequences ORDER BY id
        """)
        ).all()
        assert [tuple(row) for row in rows] == [
            (1, None, 2),
            (2, "failed", 5),
            (3, "window_exhausted", 0),
            (4, "model", 2),
            (5, "fail_open_unavailable", 0),
            (6, "failed", 5),
            (7, None, 0),
        ]

    async with engine.begin() as connection:
        await connection.run_sync(migrate)
