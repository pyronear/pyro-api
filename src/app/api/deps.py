from typing import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import JWTError, jwt

from pydantic import ValidationError

from app.api import crud, schemas
from app.security import ALGORITHM
from app.db import users
import app.config as cfg
from app.api.schemas import UserOut


reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"login/access-token",
    scopes={"me": "Read information about the current user.", "admin": "Admin rights on all routes."}
)


async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(reusable_oauth2)):
    """Dependency to use as fastapi.security.Security with scopes

    >>> @app.get("/users/me")
    >>> async def read_users_me(current_user: User = Security(get_current_user, scopes=["me"])):
    >>>     return current_user
    """

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = f"Bearer"

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )

    try:
        payload = jwt.decode(token, cfg.SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
        token_scopes = payload.get("scopes", [])
        token_data = schemas.TokenPayload(scopes=token_scopes, user_id=user_id)
    except (JWTError, ValidationError, KeyError):
        raise credentials_exception

    user = await crud.get(id=user_id, table=users)

    if user is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return UserOut(**user)
