from app.db import media, database
from .schemas import MediaIn


async def post(payload: MediaIn):
    query = media.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(id: int):
    query = media.select().where(id == media.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = media.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: MediaIn):
    query = (
        media
        .update()
        .where(id == media.c.id)
        .values(**payload.dict())
        .returning(media.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = media.delete().where(id == media.c.id)
    return await database.execute(query=query)
