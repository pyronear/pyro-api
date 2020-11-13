from typing import List, Dict, Any
from fastapi import APIRouter, Path, HTTPException
from app.api import routing, security
from app.db import accesses
from app.api.schemas import AccessBase, AccessRead, AccessAuth, AccessCreation, Cred, CredHash


router = APIRouter()


async def post_access(login: str, password: str, scopes: str) -> AccessRead:
    # Check that username does not already exist
    if await routing.fetch_entry(accesses, [('login', login)]) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"An entry with login='{login}' already exists.",
        )
    # Hash the password
    pwd = await security.hash_password(password)
    access = AccessCreation(login=login, hashed_password=pwd, scopes=scopes)
    entry = await routing.create_entry(accesses, access)

    return AccessRead(**entry)


async def update_access_pwd(payload: Cred, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    entry = await routing.get_entry(accesses, entry_id)
    # Hash the password
    pwd = await security.hash_password(payload.password)
    # Update the password
    payload = CredHash(hashed_password=pwd)
    await routing.update_entry(accesses, payload, entry_id)
    # Return non-sensitive information
    return {"login": entry["login"]}


@router.post("/", response_model=AccessRead, status_code=201)
async def create_access(payload: AccessAuth):
    return await post_access(**payload.dict())


@router.get("/{access_id}/", response_model=AccessRead)
async def get_access(access_id: int = Path(..., gt=0)):
    return await routing.get_entry(accesses, access_id)


@router.get("/", response_model=List[AccessRead])
async def fetch_accesses():
    return await routing.fetch_entries(accesses)


@router.put("/{access_id}/", response_model=AccessRead)
async def update_access(payload: AccessBase, access_id: int = Path(..., gt=0)):
    return await routing.update_entry(accesses, payload, access_id)


@router.delete("/{access_id}/", response_model=AccessRead)
async def delete_access(access_id: int = Path(..., gt=0)):
    return await routing.delete_entry(accesses, access_id)
