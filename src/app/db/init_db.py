from app import config as cfg
from app.api import crud
from app.db import accesses, users
from app.api.schemas import AccessCreation, UserCreation
from app.api.security import hash_password


async def init_db():

    # check if access login does not already exist
    entry = await crud.fetch_one(accesses, [("login", cfg.SUPERUSER_LOGIN)])
    if entry is None:

        hashed_password = await hash_password(cfg.SUPERUSER_PWD)

        access = AccessCreation(login=cfg.SUPERUSER_LOGIN, hashed_password=hashed_password, scopes="admin")
        access_entry = await crud.create_entry(accesses, access)

    return await crud.create_entry(users, UserCreation(login=cfg.SUPERUSER_LOGIN, access_id=access_entry["id"]))
