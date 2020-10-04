from app.db import installations, database
from .schemas import InstallationIn


async def post(payload: InstallationIn):
    query = installations.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(id: int):
    query = installations.select().where(id == installations.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = installations.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: InstallationIn):
    query = (
        installations
        .update()
        .where(id == installations.c.id)
        .values(**payload.dict())
        .returning(installations.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = installations.delete().where(id == installations.c.id)
    return await database.execute(query=query)
