from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.api import crud
from app.db import users
from .schemas import UserOut, UserIn


router = APIRouter()


@router.post("/", response_model=UserOut, status_code=201)
async def create_user(payload: UserIn):
    """Registers a new user"""
    user_id = await crud.post(payload, users)

    return {**payload.dict(), "id": user_id}


@router.get("/{id}/", response_model=UserOut)
async def get_user(id: int = Path(..., gt=0),):
    user = await crud.get(id, users)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.get("/", response_model=List[UserOut])
async def fetch_users():
    return await crud.fetch_all(users)


@router.put("/{id}/", response_model=UserOut)
async def update_user(payload: UserIn, id: int = Path(..., gt=0),):
    user = await crud.get(id, users)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = await crud.put(id, payload, users)

    return {**payload.dict(), "id": user_id}


@router.delete("/{id}/", response_model=UserOut)
async def delete_user(id: int = Path(..., gt=0)):
    user = await crud.get(id, users)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    await crud.delete(id, users)

    return user
