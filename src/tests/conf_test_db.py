from typing import List, Dict, Any, Mapping
from sqlalchemy import create_engine, Table
from databases import Database
from app.db import metadata
import contextlib

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
metadata.create_all(bind=engine)
database = Database(SQLALCHEMY_DATABASE_URL)


def reset_test_db():
    """
    Delete all rows from the database but keeps the schemas
    """

    with contextlib.closing(engine.connect()) as con:
        trans = con.begin()
        for table in reversed(metadata.sorted_tables):
            con.execute(table.delete())
        trans.commit()


async def populate_db(test_db: Database, table: Table, data: List[Dict[str, Any]]) -> None:
    for entry in data:
        query = table.insert().values(entry)
        await test_db.execute(query=query)


async def get_entry_in_db(test_db: Database, table: Table, entry_id: int) -> Mapping[str, Any]:
    query = table.select().where(entry_id == table.c.id)
    return await test_db.fetch_one(query=query)
