from typing import List

from fastapi import APIRouter, Path, Security, HTTPException

from app.api import routing, crud, security
from app.db import users
from app.api.schemas import UserInfo, UserRead, UserAuth, UserCreation
from app.api.deps import get_current_user


router = APIRouter()


@router.get("/me", response_model=UserRead)
async def get_my_user(me: UserRead = Security(get_current_user, scopes=["me"])):
    return me


@router.put("/update-me", response_model=UserRead)
async def update_me(payload: UserInfo, me: UserRead = Security(get_current_user, scopes=["me"])):
    return await routing.update_entry(users, payload, me.id)


@router.post("/", response_model=UserRead, status_code=201)
async def create_user(payload: UserAuth, _=Security(get_current_user, scopes=["admin"])):
    entry = await routing.fetch_entry(users, ('username', payload.username))
    if entry is not None:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists.",
        )
    pwd = await security.hash_password(payload.password)
    ####
    payload = UserCreation(username=payload.username, hashed_password=pwd, scopes=payload.scopes)
    return await routing.create_entry(users, payload)


@router.get("/{id}/", response_model=UserRead)
async def get_user(id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.get_entry(users, id)


@router.get("/", response_model=List[UserRead])
async def fetch_users(_=Security(get_current_user, scopes=["admin"])):
    return await routing.fetch_entries(users)


@router.put("/{id}/", response_model=UserRead)
async def update_user(payload: UserInfo, id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.update_entry(users, payload, id)


@router.delete("/{id}/", response_model=UserRead)
async def delete_user(id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.delete_entry(users, id)
