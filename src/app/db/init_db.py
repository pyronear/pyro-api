# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from app import config as cfg
from app.api import crud
from app.db import accesses, users
from app.api.schemas import AccessCreation, UserCreation, AccessType
from app.api.security import hash_password


async def init_db():

    login = cfg.SUPERUSER_LOGIN

    # check if access login does not already exist
    entry = await crud.fetch_one(accesses, {"login": login})
    if entry is None:

        hashed_password = await hash_password(cfg.SUPERUSER_PWD)

        access = AccessCreation(login=login, hashed_password=hashed_password, scope=AccessType.admin)
        access_entry = await crud.create_entry(accesses, access)

        await crud.create_entry(users, UserCreation(login=login, access_id=access_entry["id"]))

    return None
