# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app import config as cfg
from app.api import crud, security
from app.db import accesses
from app.schemas import Token

router = APIRouter(redirect_slashes=True)


@router.post("/access-token", response_model=Token)
async def create_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    This API follows the OAuth 2.0 specification

    If the credentials are valid, creates a new access token

    By default, the token expires after 1 hour
    """
    # Verify credentials
    entry = await crud.fetch_one(accesses, {"login": form_data.username})
    if entry is None or not await security.verify_password(form_data.password, entry["hashed_password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    # create access token using user user_id/user_scopes
    token_data = {"sub": str(entry["id"]), "scopes": entry["scope"].split()}
    if entry["scope"] == "device":
        token = await security.create_unlimited_access_token(token_data)
    else:
        token = await security.create_access_token(
            token_data, expires_delta=timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)
        )

    return {"access_token": token, "token_type": "bearer"}
