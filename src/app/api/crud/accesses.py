from typing import Dict, Any, Union, Type
from sqlalchemy import Table
from fastapi import HTTPException

from app.api import security
from app.api.crud import base
from app.api.schemas import (
    Login,
    AccessCreation,
    AccessRead,
    Cred,
    CredHash,
    UserAuth,
    UserCreation,
    DeviceCreation,
    DeviceAuth,
)


async def check_login_existence(table: Table, login: str):
    """Check that the login does not already exist, raises a 400 exception if do so."""
    if await base.fetch_one(table, {"login": login}) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"An entry with login='{login}' already exists.",
        )


async def update_login(accesses: Table, login: str, access_id: int):
    """Update access login assuming access_id exists and new login does not exist."""
    return await base.update_entry(accesses, Login(login=login), access_id)


async def post_access(accesses: Table, login: str, password: str, scopes: str) -> AccessRead:
    """Insert an access entry in the accesses table, call within a transaction to reuse returned access id."""
    await check_login_existence(accesses, login)

    # Hash the password
    pwd = await security.hash_password(password)

    access = AccessCreation(login=login, hashed_password=pwd, scopes=scopes)
    entry = await base.create_entry(accesses, access)

    return AccessRead(**entry)


async def update_access_pwd(accesses: Table, payload: Cred, entry_id: int) -> Dict[str, Any]:
    """Update the access password using provided access_id."""
    entry = await base.get_entry(accesses, entry_id)

    # Hash the password
    pwd = await security.hash_password(payload.password)

    # Update the password
    updated_payload = CredHash(hashed_password=pwd)
    await base.update_entry(accesses, updated_payload, entry_id)

    # Return non-sensitive information
    return {"login": entry["login"]}


async def create_accessed_entry(
    table: Table,
    accesses: Table,
    payload: Union[UserAuth, DeviceAuth],
    schema: Type[Union[UserCreation, DeviceCreation]],
) -> Dict:
    """Create an access and refers it to a new entry (User, Device, ...)."""
    # Ensure database consistency between tables with a transaction
    async with base.database.transaction():
        access_entry = await post_access(accesses, payload.login, payload.password, payload.scopes)
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
