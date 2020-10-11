from typing import List
from fastapi import APIRouter, Path, Depends, HTTPException, status
from app.api import routing, crud
from app.db import devices
from app.security import get_password_hash, verify_password, create_unlimited_access_token
from app.api.schemas import Device, Token
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()


async def authenticate_device(db, username: str, password: str):
    device = await crud.get(int(username), devices)
    if not device:
        return False
    device = Device(**device)
    if not verify_password(password, device.hashed_password):
        return False
    return device


@router.post("/token", response_model=Token)
async def login_device(form_data: OAuth2PasswordRequestForm = Depends()):
    device = await authenticate_device(devices, form_data.username, form_data.password)

    if not device:
        raise HTTPException(status_code=400, detail="Incorrect username or password")

    access_token = create_unlimited_access_token(data=device.id)
    return {"access_token": access_token, "token_type": "bearer"}
