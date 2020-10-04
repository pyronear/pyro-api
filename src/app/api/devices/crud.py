from app.db import devices, database
from .schemas import DeviceIn


async def post(payload: DeviceIn):
    query = devices.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(id: int):
    query = devices.select().where(id == devices.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = devices.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: DeviceIn):
    query = (
        devices
        .update()
        .where(id == devices.c.id)
        .values(**payload.dict())
        .returning(devices.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = devices.delete().where(id == devices.c.id)
    return await database.execute(query=query)
