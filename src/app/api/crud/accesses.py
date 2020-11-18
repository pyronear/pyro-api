from typing import Dict, Any
from fastapi import HTTPException
from app.api import crud, security
from app.db import accesses
from app.api.schemas import AccessRead, AccessCreation, Cred, AccessBase, CredHash


async def post_access(login: str, password: str, scopes: str) -> AccessRead:
    """Assert login does not exist, hash password, post entry into accesses table"""
    if await crud.fetch_one(accesses, [('login', login)]) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"An entry with login='{login}' already exists.",
        )

    pwd = await security.hash_password(password)
    access = AccessCreation(login=login, hashed_password=pwd, scopes=scopes)
    entry = await crud.create_entry(accesses, access)
    return AccessRead(**entry)


async def update_access_login(payload: AccessBase, entry_id: int) -> Dict[str, Any]:
    # TODO check that works
    entry = await crud.update_entry(accesses, payload, entry_id)
    # Return non-sensitive information
    return {"login": entry["login"]}


async def update_access_pwd(payload: Cred, entry_id: int) -> Dict[str, Any]:
    """hash new password & update entry"""
    pwd = await security.hash_password(payload.password)

    updated_payload = CredHash(hashed_password=pwd)
    entry = await crud.update_entry(accesses, updated_payload, entry_id)

    # Return non-sensitive information
    return {"login": entry["login"]}
