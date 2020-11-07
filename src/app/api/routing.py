from sqlalchemy import Table
from pydantic import BaseModel
from typing import Optional, Tuple, Any, List
from fastapi import HTTPException, Path
from datetime import datetime
from app.api import crud, security
from app.api.schemas import UserAuth, UserCreation, UserRead, UserCredHash, UserCred
from app.api.schemas import AccessCreation, AccessRead, AccessAuth
from app.api.schemas import DeviceAuth, DeviceCreation, DeviceOut
from app.api.schemas import HeartbeatOut, UpdatedLocation
from app.db import access as access_table


async def create_entry(table: Table, payload: BaseModel):
    entry_id = await crud.post(payload, table)
    return {**payload.dict(), "id": entry_id}


async def get_entry(table: Table, entry_id: int = Path(..., gt=0)):
    entry = await crud.get(entry_id, table)
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    return entry


async def fetch_entries(table: Table, query_filter: Optional[List[Tuple[str, Any]]] = None):
    return await crud.fetch_all(table, query_filter)


async def fetch_entry(table: Table, query_filter: List[Tuple[str, Any]]):
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


async def create_access(access_table: Table, payload: AccessAuth) -> AccessRead:
    return await _create_access(payload.login, payload.password, scopes=payload.scopes)


async def create_user(user_table: Table, payload: UserAuth) -> UserRead:
    access_entry = await _create_access(payload.username, payload.password, scopes=payload.scopes)
    user = UserCreation(username=payload.username, access_id=access_entry.id)
    return await create_entry(user_table, user)


async def create_device(device_table: Table, payload: DeviceAuth) -> DeviceOut:
    access_entry = await _create_access(payload.name, payload.password, scopes=payload.scopes)
    payload = DeviceCreation(**payload.dict(), access_id=access_entry.id)
    return await create_entry(device_table, payload)


async def update_user_pwd(user_table: Table, payload: UserCred, entry_id: int = Path(..., gt=0)):
    entry = await get_entry(user_table, entry_id)
    # Hash the password
    pwd = await security.hash_password(payload.password)
    # Update the password
    payload = UserCredHash(hashed_password=pwd)
    await crud.put(entry_id, payload, user_table)
    # Return non-sensitive information
    return {"username": entry["username"]}


async def heartbeat(device_table: Table, device: DeviceOut) -> HeartbeatOut:
    device.last_ping = datetime.utcnow()
    await update_entry(device_table, device, device.id)
    return device


async def update_location(device_table: Table, payload: UpdatedLocation, device_id: int, user_id: int):
    user_owns_device = bool(await fetch_entry(device_table, [("id", device_id), ("owner_id", user_id)]))
    if not user_owns_device:
        raise HTTPException(
            status_code=400,
            detail="You don't own this device."
        )
    device = (await get_entry(device_id, device_table))
    device.update(payload.dict())
    device = DeviceOut(**device)
    await update_entry(device_table, device, device.id)
    return device
