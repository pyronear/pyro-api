from typing import List

from fastapi import APIRouter, Path, Security

from app.api import crud
from app.db import database, users
from app.api.schemas import UserInfo, UserCreation, Cred, UserRead, UserAuth
from app.api.deps import get_current_user

from app.api.crud.accesses import post_access, update_access_pwd


router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_my_user(me: UserRead = Security(get_current_user, scopes=["me"])):
    return me


@router.put("/update-info", response_model=UserRead)
async def update_my_info(payload: UserInfo, me: UserRead = Security(get_current_user, scopes=["me"])):
    return await crud.update_entry(users, payload, me.id)


@router.put("/update-pwd", response_model=UserInfo)
async def update_my_password(payload: Cred, me: UserRead = Security(get_current_user, scopes=["me"])):
    entry = await crud.get_entry(users, me.id)
    await update_access_pwd(payload, entry["access_id"])
    return entry


@router.post("/", response_model=UserRead, status_code=201)
@database.transaction()
async def create_user(payload: UserAuth, _=Security(get_current_user, scopes=["admin"])):
    """Use transaction to insert access/user."""
    access_entry = await post_access(payload.username, payload.password, payload.scopes)
    return await crud.create_entry(users, UserCreation(username=payload.username, access_id=access_entry.id))


@router.get("/{user_id}/", response_model=UserRead)
async def get_user(user_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await crud.get_entry(users, user_id)


@router.get("/", response_model=List[UserRead])
async def fetch_users(_=Security(get_current_user, scopes=["admin"])):
    return await crud.fetch_all(users)


@router.put("/{user_id}/", response_model=UserRead)
async def update_user(
    payload: UserInfo,
    user_id: int = Path(..., gt=0),
    _=Security(get_current_user, scopes=["admin"])
):
    return await crud.update_entry(users, payload, user_id)


@router.put("/{user_id}/pwd", response_model=UserInfo)
async def update_user_password(
    payload: Cred,
    user_id: int = Path(..., gt=0),
    _=Security(get_current_user, scopes=["admin"])
):
    # Check that user does exist
    entry = await crud.get_entry(users, user_id)
    # Update the credentials
    await update_access_pwd(payload, entry["access_id"])
    return entry


@router.delete("/{user_id}/", response_model=UserRead)
async def delete_user(user_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await crud.delete_entry(users, user_id)
