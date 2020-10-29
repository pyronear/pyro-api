from fastapi import HTTPException, Path
from app.api import crud
from sqlalchemy import Table
from pydantic import BaseModel
from typing import Optional, Tuple, Any


async def create_entry(table: Table, payload: BaseModel):
    entry_id = await crud.post(payload, table)

    return {**payload.dict(), "id": entry_id}


async def get_entry(table: Table, id: int = Path(..., gt=0)):
    entry = await crud.get(id, table)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


async def fetch_entries(table: Table, query_filter: Optional[Tuple[str, Any]] = None):
    return await crud.fetch_all(table, query_filter)


async def update_entry(table: Table, payload: BaseModel, id: int = Path(..., gt=0)):
    await get_entry(table, id)
    entry_id = await crud.put(id, payload, table)

    return {**payload.dict(), "id": entry_id}


async def delete_entry(table: Table, id: int = Path(..., gt=0)):
    entry = await get_entry(table, id)
    await crud.delete(id, table)

    return entry
