# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from app import config as cfg
from app.api import crud
from app.api.security import hash_password
from app.models import AccessType
from app.schemas import AccessCreation, GroupIn, UserCreation

from .tables import accesses, groups, users

__all__ = ["init_db"]


async def init_db():

    login = cfg.SUPERUSER_LOGIN

    # check if access login does not already exist
    entry = await crud.fetch_one(accesses, {"login": login})
    if entry is None:

        hashed_password = await hash_password(cfg.SUPERUSER_PWD)

        admin_group = GroupIn(name="admins")
        group_entry = await crud.create_entry(groups, admin_group)

        access = AccessCreation(
            login=login, hashed_password=hashed_password, scope=AccessType.admin, group_id=group_entry["id"]
        )
        access_entry = await crud.create_entry(accesses, access)

        await crud.create_entry(users, UserCreation(login=login, access_id=access_entry["id"]))

    return None
