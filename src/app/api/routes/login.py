from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api import routing, security
from app.api.schemas import Token
from app.db import access
from app import config as cfg

router = APIRouter()


@router.post("/access-token", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    entry = await routing.fetch_entry(access, ('username', form_data.username))
    if entry is None or not await security.verify_password(form_data.password, entry['hashed_password']):
        raise HTTPException(status_code=400, detail="Incorrect login or password")
    # create access token using user user_id/user_scopes
    token_data = {"sub": str(entry['id']), "scopes": entry['scopes'].split()}
    is_device = entry["scopes"] == "device"
    if is_device:
        token = await security.create_unlimited_access_token(token_data)
    else:
        token = await security.create_access_token(token_data,
                                                   expires_delta=timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
                                                   )

    return {"access_token": token, "token_type": "bearer"}
