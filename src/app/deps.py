from fastapi import Depends, HTTPException, status, Security
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from jose import jwt, JWTError

from app import config, security
from app.db import devices
from app.api import crud
from app.api.schemas import Device, TokenPayload
from pydantic import ValidationError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="authorization/token",
    scopes={"heartbeat": "Send heartbeat signal to the API for only one device"},
)


async def get_current_device(
    security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
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
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[security.ALGORITHM])
        sub: int = payload.get("sub")
        if sub is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        
        token_data = TokenPayload(**payload)
    except (JWTError, ValidationError):
        raise credentials_exception
    device = await crud.get(token_data.sub, devices)
    if device is None:
        raise credentials_exception

    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return device


async def get_current_active_device(current_device: Device = Security(get_current_device, scopes=["heartbeat"])) -> Device:
    # If one include the notion of active/disabled, the following code may be useful.
    # if current_device.disabled:
    #     raise HTTPException(status_code=400, detail="Inactive device")
    return current_device
