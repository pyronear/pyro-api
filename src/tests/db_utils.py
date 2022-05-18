# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import contextlib
from typing import Any, Dict, List, Mapping

from databases import Database
from sqlalchemy import Table, create_engine
from sqlalchemy.orm import sessionmaker

import app.config as cfg
from app.db import metadata

SQLALCHEMY_DATABASE_URL = cfg.TEST_DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
metadata.create_all(bind=engine)
database = Database(SQLALCHEMY_DATABASE_URL)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


async def reset_test_db():
    """
    Delete all rows from the database but keeps the schemas
    """

    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(metadata.sorted_tables):
            con.execute(table.delete())
            con.execute(f"ALTER SEQUENCE {table}_id_seq RESTART WITH 1")
        trans.commit()


async def fill_table(test_db: Database, table: Table, entries: List[Dict[str, Any]], remove_ids: bool = True) -> None:
    """
    Directly insert data into the DB table. Set remove_ids to True by default as the id sequence pointer
    are not incremented if the "id" field is included
    """
    if remove_ids:
        entries = [{k: v for k, v in x.items() if k != "id"} for x in entries]

    query = table.insert().values(entries)
    await test_db.execute(query=query)


async def get_entry(test_db: Database, table: Table, entry_id: int) -> Mapping[str, Any]:
    query = table.select().where(entry_id == table.c.id)
    return await test_db.fetch_one(query=query)
