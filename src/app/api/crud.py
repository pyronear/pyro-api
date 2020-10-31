from typing import Optional
from app.db import database
from sqlalchemy import Table, and_
from pydantic import BaseModel
from fastapi import HTTPException

from app.api.schemas import UserCreate, UserOut, UserInDb, DeviceOut, HeartbeatOut, UpdatedLocation
from app.db import users, devices
from datetime import datetime
from app import security


async def post(payload: BaseModel, table: Table):
    query = table.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(id: int, table: Table):
    query = table.select().where(id == table.c.id)
    return await database.fetch_one(query=query)


async def fetch_all(table: Table):
    query = table.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: BaseModel, table: Table):
    query = (
        table
        .update()
        .where(id == table.c.id)
        .values(**payload.dict())
        .returning(table.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int, table: Table):
    query = table.delete().where(id == table.c.id)
    return await database.execute(query=query)


class DevideCRUD:

    async def user_owns_device(self, device_id: int, owner_id: int) -> bool:
        query = devices.select().where(and_(devices.c.id == device_id, devices.c.owner_id == owner_id))
        return bool(await database.fetch_one(query=query))

    async def fetch_by_owner(self, owner_id: int):
        query = devices.select().where(devices.c.owner_id == owner_id)
        return await database.fetch_all(query=query)

    async def fetch_by_user(self, user_id: int):
        query = devices.select().where(devices.c.user_id == user_id)
        return await database.fetch_one(query=query)

    async def heartbeat(self, user_id: int) -> HeartbeatOut:
        device = DeviceOut(** await self.fetch_by_user(user_id))
        device.last_ping = datetime.utcnow()
        await put(device.id, device, devices)
        return device

    async def update_location(self, payload: UpdatedLocation, device_id: int, user_id: int):
        user_owns_device = await self.user_owns_device(device_id, user_id)
        if not user_owns_device:
            raise HTTPException(
                status_code=400,
                detail="You don't own this device."
            )
        device = DeviceOut(** await get(device_id, devices))
        device.last_lat = payload.lat
        device.last_lon = payload.lon
        device.last_yaw = payload.yaw
        device.last_pitch = payload.pitch
        await put(device.id, device, devices)
        return device


class UserCRUD:

    async def create(self, user_in: UserCreate) -> UserOut:
        pwd = await security.get_password_hash(user_in.password)
        query = users.insert().values(username=user_in.username, hashed_password=pwd, scopes=user_in.scopes)
        user_id = await database.execute(query=query)
        return UserOut(id=user_id, username=user_in.username)

    async def get_by_username(self, username: str) -> UserInDb:
        query = users.select().where(username == users.c.username)
        record = await database.fetch_one(query=query)
        if record is None:
            return None
        return UserInDb(**record)

    async def authenticate(self, username: str, password: str) -> Optional[UserInDb]:
        usr = await self.get_by_username(username=username)

        if not usr:
            return None
        if not await security.verify_password(password, usr.hashed_password):
            return None
        return usr


user = UserCRUD()
device = DevideCRUD()
