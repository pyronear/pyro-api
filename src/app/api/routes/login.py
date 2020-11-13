from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api import routing, security
from app.api.schemas import Token
from app.db import accesses
from app import config as cfg

router = APIRouter()


@router.post("/access-token", response_model=Token)
async def create_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Verify credentials
    entry = await routing.fetch_entry(accesses, [('login', form_data.username)])
    if entry is None or not await security.verify_password(form_data.password, entry['hashed_password']):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    # create access token using user user_id/user_scopes
    token_data = {"sub": str(entry['id']), "scopes": entry['scopes'].split()}
    if entry["scopes"] == "device":
        token = await security.create_unlimited_access_token(token_data)
    else:
        token = await security.create_access_token(token_data,
                                                   expires_delta=timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
                                                   )

    return {"access_token": token, "token_type": "bearer"}
