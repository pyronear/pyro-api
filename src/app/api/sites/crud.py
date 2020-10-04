from app.db import sites, database
from .schemas import SiteIn


async def post(payload: SiteIn):
    query = sites.insert().values(**payload.dict())
    return await database.execute(query=query)


async def get(id: int):
    query = sites.select().where(id == sites.c.id)
    return await database.fetch_one(query=query)


async def get_all():
    query = sites.select()
    return await database.fetch_all(query=query)


async def put(id: int, payload: SiteIn):
    query = (
        sites
        .update()
        .where(id == sites.c.id)
        .values(**payload.dict())
        .returning(sites.c.id)
    )
    return await database.execute(query=query)


async def delete(id: int):
    query = sites.delete().where(id == sites.c.id)
    return await database.execute(query=query)
