from typing import Optional, Tuple, Any
from app.db import database
from sqlalchemy import Table
from pydantic import BaseModel


async def post(payload: BaseModel, table: Table):
    query = table.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(entry_id: int, table: Table):
    query = table.select().where(entry_id == table.c.id)
    return await database.fetch_one(query=query)


async def fetch_all(table: Table, query_filter: Optional[Tuple[str, Any]] = None):
    query = table.select()
    if isinstance(query_filter, tuple):
        query = query.where(getattr(table.c, query_filter[0]) == query_filter[1])
    return await database.fetch_all(query=query)


async def fetch_one(table: Table, query_filter: Tuple[str, Any]):
    query = table.select().where(getattr(table.c, query_filter[0]) == query_filter[1])
    return await database.fetch_one(query=query)


async def put(entry_id: int, payload: BaseModel, table: Table):
    query = (
        table
        .update()
        .where(entry_id == table.c.id)
        .values(**payload.dict())
        .returning(table.c.id)
    )
    return await database.execute(query=query)


async def delete(entry_id: int, table: Table):
    query = table.delete().where(entry_id == table.c.id)
    return await database.execute(query=query)
