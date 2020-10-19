from typing import Optional
from app.db import database
from sqlalchemy import Table
from pydantic import BaseModel

from app.api.schemas import UserCreate, UserOut, UserInDb, DeviceOut
from app.db import users, devices
from app.security import get_password_hash, verify_password


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

    async def fetch_by_owner(self, owner_id: int):
        query = devices.select().where(devices.c.owner_id == owner_id)
        return await database.fetch_all(query=query)


class UserCRUD:

    async def create(self, user_in: UserCreate) -> UserOut:
        pwd = await get_password_hash(user_in.password)
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
        if not await verify_password(password, usr.hashed_password):
            return None
        return usr


user = UserCRUD()
device = DevideCRUD()

