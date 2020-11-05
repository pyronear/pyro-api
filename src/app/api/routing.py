from sqlalchemy import Table
from pydantic import BaseModel
from typing import Optional, Tuple, Any
from fastapi import HTTPException, Path

from app.api import crud, security
from app.api.schemas import UserAuth, UserCreation


async def create_entry(table: Table, payload: BaseModel):
    entry_id = await crud.post(payload, table)
    return {**payload.dict(), "id": entry_id}


async def get_entry(table: Table, entry_id: int = Path(..., gt=0)):
    entry = await crud.get(entry_id, table)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


async def fetch_entries(table: Table, query_filter: Optional[Tuple[str, Any]] = None):
    return await crud.fetch_all(table, query_filter)


async def fetch_entry(table: Table, query_filter: Tuple[str, Any]):
    return await crud.fetch_one(table, query_filter)


async def update_entry(table: Table, payload: BaseModel, entry_id: int = Path(..., gt=0)):
    await get_entry(table, entry_id)
    entry_id = await crud.put(entry_id, payload, table)

    return {**payload.dict(), "id": entry_id}


async def delete_entry(table: Table, entry_id: int = Path(..., gt=0)):
    entry = await get_entry(table, entry_id)
    await crud.delete(entry_id, table)

    return entry


async def create_user(user_table: Table, payload: UserAuth):
    # Check that username does not already exist
    if await fetch_entry(user_table, ('username', payload.username)) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"An entry with username='{payload.username}' already exists.",
        )

    # Hash the password
    pwd = await security.hash_password(payload.password)
    payload = UserCreation(username=payload.username, hashed_password=pwd, scopes=payload.scopes)
    return await create_entry(user_table, payload)
