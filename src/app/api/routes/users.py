from typing import List

from fastapi import APIRouter, Path, Security, HTTPException

from app.api import routing, security
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
    return await routing.create_user(users, payload)


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
