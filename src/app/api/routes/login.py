from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from app.api import crud, schemas
from app import config as cfg
from app.security import create_access_token

router = APIRouter()


@router.post("/access-token", response_model=schemas.Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await crud.user.authenticate(username=form_data.username, password=form_data.password)

    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=cfg.ACCESS_TOKEN_EXPIRE_MINUTES)

    # create access token using user user_id/user_scopes
    return {
        "access_token": await create_access_token(
            {"sub": str(user.id), "scopes": user.scopes.split()},
            expires_delta=access_token_expires,
        ),
        "token_type": "bearer",
    }
