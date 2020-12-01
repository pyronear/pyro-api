from typing import List, Dict, Any
from fastapi import APIRouter, Path, HTTPException
from app.api import crud, security
from app.db import accesses
from app.api.schemas import AccessBase, AccessRead, AccessAuth, AccessCreation, Cred, CredHash


router = APIRouter()


async def post_access(login: str, password: str, scopes: str) -> AccessRead:
    # Check that the login does not already exist
    if await crud.fetch_one(accesses, {'login': login}) is not None:
        raise HTTPException(
            status_code=400,
            detail=f"An entry with login='{login}' already exists.",
        )
    # Hash the password
    pwd = await security.hash_password(password)
    access = AccessCreation(login=login, hashed_password=pwd, scopes=scopes)
    entry = await crud.create_entry(accesses, access)

    return AccessRead(**entry)


async def update_access_pwd(payload: Cred, entry_id: int = Path(..., gt=0)) -> Dict[str, Any]:
    entry = await crud.get_entry(accesses, entry_id)
    # Hash the password
    pwd = await security.hash_password(payload.password)
    # Update the password
    payload = CredHash(hashed_password=pwd)
    await crud.update_entry(accesses, payload, entry_id)
    # Return non-sensitive information
    return {"login": entry["login"]}


@router.post("/", response_model=AccessRead, status_code=201, summary="Create a new access")
async def create_access(payload: AccessAuth):
    """
    If the provided login does not exist, creates a new access based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await post_access(payload.login, payload.password, payload.scopes)


@router.get("/{access_id}/", response_model=AccessRead, summary="Get information about a specific access")
async def get_access(access_id: int = Path(..., gt=0)):
    """
    Based on a access_id, retrieves information about the specified access
    """
    return await crud.get_entry(accesses, access_id)


@router.get("/", response_model=List[AccessRead], summary="Get the list of all accesses")
async def fetch_accesses():
    """
    Retrieves the list of all accesses and their information
    """
    return await crud.fetch_all(accesses)


@router.put("/{access_id}/", response_model=AccessRead, summary="Update information about a specific access")
async def update_access(payload: AccessBase, access_id: int = Path(..., gt=0)):
    """
    Based on a access_id, updates information about the specified access
    """
    return await crud.update_entry(accesses, payload, access_id)


@router.delete("/{access_id}/", response_model=AccessRead, summary="Delete a specific access")
async def delete_access(access_id: int = Path(..., gt=0)):
    """
    Based on a access_id, deletes the specified access
    """
    return await crud.delete_entry(accesses, access_id)
