from app.db import alerts, database
from .schemas import AlertIn


async def post(payload: AlertIn):
    query = alerts.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(id: int):
    query = alerts.select().where(id == alerts.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = alerts.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: AlertIn):
    query = (
        alerts
        .update()
        .where(id == alerts.c.id)
        .values(**payload.dict())
        .returning(alerts.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = alerts.delete().where(id == alerts.c.id)
    return await database.execute(query=query)
