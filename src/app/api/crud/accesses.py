# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Any, Dict, Type, Union

from fastapi import HTTPException, status
from sqlalchemy import Table

from app.api import security
from app.api.crud import base
from app.schemas import (
    AccessCreation,
    AccessRead,
    Cred,
    CredHash,
    DeviceAuth,
    DeviceCreation,
    Login,
    UserAuth,
    UserCreation,
)


async def get_access_group_id(table: Table, access_id: int) -> int:
    return (await base.get_entry(table, access_id))["group_id"]


async def check_login_existence(table: Table, login: str):
    """Check that the login does not already exist, raises a 400 exception if do so."""
    if await base.fetch_one(table, {"login": login}) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"An entry with login='{login}' already exists.",
        )


async def update_login(accesses: Table, login: str, access_id: int):
    """Update access login assuming access_id exists and new login does not exist."""
    return await base.update_entry(accesses, Login(login=login), access_id)


async def post_access(accesses: Table, login: str, password: str, scope: str, group_id: int) -> AccessRead:
    """Insert an access entry in the accesses table, call within a transaction to reuse returned access id."""
    await check_login_existence(accesses, login)

    # Hash the password
    pwd = await security.hash_password(password)

    access = AccessCreation(login=login, hashed_password=pwd, scope=scope, group_id=group_id)
    entry = await base.create_entry(accesses, access)

    return AccessRead(**entry)


async def update_access_pwd(accesses: Table, payload: Cred, access_id: int) -> None:
    """Update the access password using provided access_id."""
    # Update the access entry with the hashed password
    updated_payload = CredHash(hashed_password=await security.hash_password(payload.password))

    await base.update_entry(accesses, updated_payload, access_id)  # update & check if access_id exists


async def create_accessed_entry(
    table: Table,
    accesses: Table,
    payload: Union[UserAuth, DeviceAuth],
    schema: Type[Union[UserCreation, DeviceCreation]],
) -> Dict:
    """Create an access and refers it to a new entry (User, Device, ...)."""
    # Ensure database consistency between tables with a transaction
    async with base.database.transaction():
        access_entry = await post_access(accesses, payload.login, payload.password, payload.scope, payload.group_id)
        entry = await base.create_entry(table, schema(**payload.dict(), access_id=access_entry.id))

    return entry


async def update_accessed_entry(table: Table, accesses: Table, entry_id: int, payload: Any):
    """Update an entry with a special treatment regarding login: if login is set -> update corresponding access."""
    # Ensure database consistency between tables with a transaction (login must remain the same in table & accesses)
    async with base.database.transaction():

        # Handle access update only if login is set
        if payload.login is not None:

            # Need to retrieve access_id from entry
            origin_entry = await base.get_entry(table, entry_id)  # assert entry exist

            # Update corresponding access only if login need to change
            if payload.login != origin_entry["login"]:
                await check_login_existence(accesses, payload.login)  # assert new login does not exist in accesses
                await update_login(accesses, payload.login, origin_entry["access_id"])

        # Update entry with input payload
        entry = await base.update_entry(table, payload, entry_id)

    return entry


async def delete_accessed_entry(table: Table, accesses: Table, entry_id: int):
    """Delete an entry (User, Device, ...) and the corresponding access."""
    # Ensure database consistency between tables with a transaction
    async with base.database.transaction():
        entry = await base.delete_entry(table, entry_id)
        await base.delete_entry(accesses, entry["access_id"])

    return entry
