import contextlib
from typing import List, Dict, Any, Mapping
from sqlalchemy import create_engine, Table
from databases import Database

from app.db import metadata
import app.config as cfg

SQLALCHEMY_DATABASE_URL = cfg.TEST_DATABASE_URL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL
)
metadata.create_all(bind=engine)
database = Database(SQLALCHEMY_DATABASE_URL)


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


async def populate_db(test_db: Database, table: Table, data: List[Dict[str, Any]], remove_ids: bool = True) -> None:
    """
    Directly insert data into the DB table. Set remove_ids to True by default as the id sequence pointer
    are not incremented if the "id" field is included
    """
    if remove_ids:
        data = [{k: v for k, v in x.items() if k != "id"} for x in data]

    for entry in data:
        query = table.insert().values(entry)
        await test_db.execute(query=query)


async def get_entry_in_db(test_db: Database, table: Table, entry_id: int) -> Mapping[str, Any]:
    query = table.select().where(entry_id == table.c.id)
    return await test_db.fetch_one(query=query)
