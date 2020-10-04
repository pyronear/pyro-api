from app.db import events, database
from .schemas import EventIn


async def post(payload: EventIn):
    query = events.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(id: int):
    query = events.select().where(id == events.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = events.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: EventIn):
    query = (
        events
        .update()
        .where(id == events.c.id)
        .values(**payload.dict())
        .returning(events.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = events.delete().where(id == events.c.id)
    return await database.execute(query=query)
