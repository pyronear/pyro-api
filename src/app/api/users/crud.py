from app.db import users, database
from .schemas import UserIn


async def post(payload: UserIn):
    query = users.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(id: int):
    query = users.select().where(id == users.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = users.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: UserIn):
    query = (
        users
        .update()
        .where(id == users.c.id)
        .values(**payload.dict())
        .returning(users.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = users.delete().where(id == users.c.id)
    return await database.execute(query=query)
