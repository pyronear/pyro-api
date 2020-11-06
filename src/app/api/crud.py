from typing import Optional, Tuple, Any
from app.db import database
from sqlalchemy import Table, and_
from pydantic import BaseModel
from fastapi import HTTPException

from app.api.schemas import DeviceOut, HeartbeatOut, UpdatedLocation
from app.db import devices
from datetime import datetime


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


class DeviceCRUD:

    @classmethod
    async def heartbeat(cls, device: DeviceOut) -> HeartbeatOut:
        device.last_ping = datetime.utcnow()
        await put(device.id, device, devices)
        return device

    @classmethod
    async def user_owns_device(cls, device_id: int, owner_id: int) -> bool:
        query = devices.select().where(and_(devices.c.id == device_id, devices.c.owner_id == owner_id))
        return bool(await database.fetch_one(query=query))

    @classmethod
    async def update_location(cls, payload: UpdatedLocation, device_id: int, user_id: int):
        user_owns_device = await cls.user_owns_device(device_id, user_id)
        if not user_owns_device:
            raise HTTPException(
                status_code=400,
                detail="You don't own this device."
            )
        device = (await get(device_id, devices))
        device.update(payload.dict())
        device = DeviceOut(**device)
        await put(device.id, device, devices)
        return device
