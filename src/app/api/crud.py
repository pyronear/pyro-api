from typing import Optional, Any, List, Dict, Mapping
from app.db import database
from sqlalchemy import Table
from pydantic import BaseModel
from fastapi import HTTPException, Path


async def post(payload: BaseModel, table: Table) -> int:
    query = table.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(entry_id: int, table: Table) -> Mapping[str, Any]:
    query = table.select().where(entry_id == table.c.id)
    return await database.fetch_one(query=query)


async def fetch_all(table: Table, query_filters: Optional[Dict[str, Any]] = None) -> List[Mapping[str, Any]]:
    query = table.select()
    if isinstance(query_filters, dict):
        for query_filter_key, query_filter_value in query_filters.items():
            query = query.where(getattr(table.c, query_filter_key) == query_filter_value)
    return await database.fetch_all(query=query)


async def fetch_one(table: Table, query_filters: Dict[str, Any]) -> Mapping[str, Any]:
    query = table.select()
    for query_filter_key, query_filter_value in query_filters.items():
        query = query.where(getattr(table.c, query_filter_key) == query_filter_value)
    return await database.fetch_one(query=query)


async def put(entry_id: int, payload: BaseModel, table: Table) -> int:
    query = (
        table
        .update()
        .where(entry_id == table.c.id)
        .values(**payload.dict())
        .returning(table.c.id)
    )
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
        raise HTTPException(status_code=404, detail="Entry not found")

    return dict(entry)


async def update_entry(table: Table, payload: BaseModel, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    entry_id = await put(entry_id, payload, table)

    if not isinstance(entry_id, int):
        raise HTTPException(status_code=404, detail="Entry not found")

    return {**payload.dict(), "id": entry_id}


async def delete_entry(table: Table, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    entry = await get_entry(table, entry_id)
    await delete(entry_id, table)

    return entry


async def fetch_ongoing_alerts(table: Table, query_filters: Dict[str, Any],
                               excluded_events_filter: Dict[str, Any]) -> List[Mapping[str, Any]]:
    query = table.select()
    if isinstance(query_filters, dict):
        for query_filter_key, query_filter_value in query_filters.items():
            query = query.where(getattr(table.c, query_filter_key) == query_filter_value)

    # Should be performed using a sqlalchemy accessor. E.g: alert_event_end_ts is None
    # To do in another review
    all_closed_events = table.select().with_only_columns([table.c.event_id])
    if isinstance(excluded_events_filter, dict):
        for query_filter_key, query_filter_value in excluded_events_filter.items():
            all_closed_events = all_closed_events.where(getattr(table.c, query_filter_key) == query_filter_value)
    query = query.where(~getattr(table.c, "event_id").in_(all_closed_events))

    return await database.fetch_all(query=query)
