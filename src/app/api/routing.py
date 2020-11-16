from sqlalchemy import Table
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
from fastapi import HTTPException, Path
from datetime import datetime
from app.api import crud, security
from app.api.schemas import (UserAuth, UserCreation, UserRead, CredHash, Cred,
                             AccessCreation, AccessRead, AccessAuth,
                             DeviceAuth, DeviceCreation, DeviceOut,
                             HeartbeatOut, DefaultPosition)
from app.db import accesses as access_table


async def create_entry(table: Table, payload: BaseModel):
    entry_id = await crud.post(payload, table)
    return {**payload.dict(), "id": entry_id}


async def get_entry(table: Table, entry_id: int = Path(..., gt=0)):
    entry = await crud.get(entry_id, table)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


async def fetch_entries(table: Table, query_filter: Optional[Dict[str, Any]] = None):
    return await crud.fetch_all(table, query_filter)


async def fetch_entry(table: Table, query_filter: Dict[str, Any]):
    return await crud.fetch_one(table, query_filter)


async def update_entry(table: Table, payload: BaseModel, entry_id: int = Path(..., gt=0)):
    await get_entry(table, entry_id)
    entry_id = await crud.put(entry_id, payload, table)

    return {**payload.dict(), "id": entry_id}


async def delete_entry(table: Table, entry_id: int = Path(..., gt=0)):
    entry = await get_entry(table, entry_id)
    await crud.delete(entry_id, table)

    return entry


async def _create_access(login: str, password: str, scopes: str) -> AccessRead:
    # Check that username does not already exist
    if await fetch_entry(access_table, [('login', login)]) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"An entry with login='{login}' already exists.",
        )
    # Hash the password
    pwd = await security.hash_password(password)
    access = AccessCreation(login=login, hashed_password=pwd, scopes=scopes)
    access_entry = AccessRead(** await create_entry(access_table, access))
    return access_entry


async def create_access(payload: AccessAuth) -> AccessRead:
    return await _create_access(payload.login, payload.password, scopes=payload.scopes)


async def create_user(user_table: Table, payload: UserAuth) -> UserRead:
    access_entry = await _create_access(payload.username, payload.password, scopes=payload.scopes)
    user = UserCreation(username=payload.username, access_id=access_entry.id)
    return await create_entry(user_table, user)


async def create_device(device_table: Table, payload: DeviceAuth) -> DeviceOut:
    access_entry = await _create_access(payload.name, payload.password, scopes=payload.scopes)
    payload = DeviceCreation(**payload.dict(), access_id=access_entry.id)
    return await create_entry(device_table, payload)


async def update_access_pwd(payload: Cred, entry_id: int = Path(..., gt=0)):
    entry = await get_entry(access_table, entry_id)
    # Hash the password
    pwd = await security.hash_password(payload.password)
    # Update the password
    payload = CredHash(hashed_password=pwd)
    await crud.put(entry_id, payload, access_table)
    # Return non-sensitive information
    return {"login": entry["login"]}


async def update_pwd(table: Table, payload: Cred, entry_id: int = Path(..., gt=0)):
    entry = await get_entry(table, entry_id)
    await update_access_pwd(payload, entry["access_id"])
    return entry


async def heartbeat(device_table: Table, device: DeviceOut) -> HeartbeatOut:
    device.last_ping = datetime.utcnow()
    await update_entry(device_table, device, device.id)
    return device


async def update_location(device_table: Table, payload: DefaultPosition, device_id: int, user_id: int):
    user_owns_device = bool(await fetch_entry(device_table, [("id", device_id), ("owner_id", user_id)]))
    if not user_owns_device:
        raise HTTPException(
            status_code=400,
            detail="Permission denied"
        )
    device = (await get_entry(device_id, device_table))
    device.update(payload.dict())
    device = DeviceOut(**device)
    await update_entry(device_table, device, device.id)
    return device
