from typing import List

from fastapi import APIRouter, Path, Security, HTTPException

from app.api import routing
from app.db import users
from app.api.schemas import UserOut, UserCreate, UserIn
from app.api.deps import get_current_user
from app.api import crud

router = APIRouter()


@router.get("/me", response_model=UserOut)
async def get_my_user(me: UserOut = Security(get_current_user, scopes=["me"])):
    return me


@router.put("/update-me", response_model=UserOut)
async def update_me(payload: UserIn, me: UserOut = Security(get_current_user, scopes=["me"])):
    return await routing.update_entry(users, payload, me.id)


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(user_in: UserCreate, _=Security(get_current_user, scopes=["admin"])):
    user = await crud.user.get_by_username(username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists.",
        )
    return await crud.user.create(user_in)


@router.get("/{id}/", response_model=UserOut)
async def get_user(id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.get_entry(users, id)


@router.get("/", response_model=List[UserOut])
async def fetch_users(_=Security(get_current_user, scopes=["admin"])):
    return await routing.fetch_entries(users)


@router.put("/{id}/", response_model=UserOut)
async def update_user(payload: UserIn, id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.update_entry(users, payload, id)


@router.delete("/{id}/", response_model=UserOut)
async def delete_user(id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.delete_entry(users, id)
