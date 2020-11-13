from sqlalchemy import Table
from pydantic import BaseModel
from typing import Optional, Tuple, Any, List, Dict
from fastapi import HTTPException, Path
from app.api import crud


async def create_entry(table: Table, payload: BaseModel) -> Dict[str, Any]:
    entry_id = await crud.post(payload, table)
    return {**payload.dict(), "id": entry_id}


async def get_entry(table: Table, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    entry = await crud.get(entry_id, table)
    if entry is None:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


async def fetch_entries(table: Table, query_filter: Optional[List[Tuple[str, Any]]] = None) -> List[Dict[str, Any]]:
    return await crud.fetch_all(table, query_filter)


async def fetch_entry(table: Table, query_filter: List[Tuple[str, Any]]) -> Dict[str, Any]:
    return await crud.fetch_one(table, query_filter)


async def update_entry(table: Table, payload: BaseModel, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    await get_entry(table, entry_id)
    entry_id = await crud.put(entry_id, payload, table)

    return {**payload.dict(), "id": entry_id}


async def delete_entry(table: Table, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    entry = await get_entry(table, entry_id)
    await crud.delete(entry_id, table)

    return entry
