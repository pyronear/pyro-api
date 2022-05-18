# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import Any, Dict, List, Mapping, Optional

from fastapi import HTTPException, Path, status
from pydantic import BaseModel
from sqlalchemy import Table

from app.db import database

__all__ = [
    "post",
    "get",
    "fetch_all",
    "fetch_one",
    "put",
    "delete",
    "create_entry",
    "get_entry",
    "update_entry",
    "delete_entry",
]


async def post(payload: BaseModel, table: Table) -> int:
    query = table.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(entry_id: int, table: Table) -> Mapping[str, Any]:
    query = table.select().where(entry_id == table.c.id)
    return await database.fetch_one(query=query)


async def fetch_all(
    table: Table,
    query_filters: Optional[Dict[str, Any]] = None,
    exclusions: Optional[Dict[str, Any]] = None,
    limit: int = 50,
) -> List[Mapping[str, Any]]:
    query = table.select().order_by(table.c.id.desc())
    if isinstance(query_filters, dict):
        for key, value in query_filters.items():
            query = query.where(getattr(table.c, key) == value)

    if isinstance(exclusions, dict):
        for key, value in exclusions.items():
            query = query.where(getattr(table.c, key) != value)
    return await database.fetch_all(query=query.limit(limit))


async def fetch_one(table: Table, query_filters: Dict[str, Any]) -> Mapping[str, Any]:
    query = table.select()
    for query_filter_key, query_filter_value in query_filters.items():
        query = query.where(getattr(table.c, query_filter_key) == query_filter_value)
    return await database.fetch_one(query=query)


async def put(entry_id: int, payload: Dict, table: Table) -> int:
    query = table.update().where(entry_id == table.c.id).values(**payload).returning(table.c.id)
    return await database.execute(query=query)


async def delete(entry_id: int, table: Table) -> None:
    query = table.delete().where(entry_id == table.c.id)
    await database.execute(query=query)


async def create_entry(table: Table, payload: BaseModel) -> Dict[str, Any]:
    entry_id = await post(payload, table)
    return {**payload.dict(), "id": entry_id}


async def get_entry(table: Table, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    entry = await get(entry_id, table)
    if entry is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table {table.name} has no entry with id={entry_id}"
        )

    return dict(entry)


async def update_entry(
    table: Table, payload: BaseModel, entry_id: int = Path(..., gt=0), only_specified: bool = True
) -> Dict[str, Any]:
    payload_dict = payload.dict()

    if only_specified:
        # Dont update columns for null fields
        payload_dict = {k: v for k, v in payload_dict.items() if v is not None}

    _id = await put(entry_id, payload_dict, table)

    if not isinstance(_id, int):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Table {table.name} has no entry with id={entry_id}"
        )

    if only_specified:
        # Retrieve complete record values
        return dict(await get(entry_id, table))
    else:
        return {**payload.dict(), "id": entry_id}


async def delete_entry(table: Table, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    entry = await get_entry(table, entry_id)
    await delete(entry_id, table)

    return entry
