# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import logging
from typing import Dict, Type, TypeVar, Union, cast

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, SecurityScopes
from httpx import AsyncClient, HTTPStatusError
from jwt import DecodeError, ExpiredSignatureError, InvalidSignatureError
from jwt import decode as jwt_decode
from pydantic import BaseModel, ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.crud import AlertCRUD, CameraCRUD, DetectionCRUD, OrganizationCRUD, SequenceCRUD, UserCRUD, WebhookCRUD
from app.crud.crud_pose import PoseCRUD
from app.db import get_session
from app.models import User, UserRole
from app.schemas.login import TokenPayload

JWTTemplate = TypeVar("JWTTemplate")
logger = logging.getLogger("uvicorn.error")

__all__ = ["get_user_crud"]

# Scope definition
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/creds",
    scopes={
        UserRole.ADMIN: "Admin rights on all routes.",
        UserRole.AGENT: "Read access on available information and write access on owned resources.",
        UserRole.USER: "Read access on available information.",
    },
)


def get_user_crud(session: AsyncSession = Depends(get_session)) -> UserCRUD:
    return UserCRUD(session=session)


def get_camera_crud(session: AsyncSession = Depends(get_session)) -> CameraCRUD:
    return CameraCRUD(session=session)


def get_pose_crud(session: AsyncSession = Depends(get_session)) -> PoseCRUD:
    return PoseCRUD(session=session)


def get_detection_crud(session: AsyncSession = Depends(get_session)) -> DetectionCRUD:
    return DetectionCRUD(session=session)


def get_organization_crud(session: AsyncSession = Depends(get_session)) -> OrganizationCRUD:
    return OrganizationCRUD(session=session)


def get_webhook_crud(session: AsyncSession = Depends(get_session)) -> WebhookCRUD:
    return WebhookCRUD(session=session)


def get_sequence_crud(session: AsyncSession = Depends(get_session)) -> SequenceCRUD:
    return SequenceCRUD(session=session)


def get_alert_crud(session: AsyncSession = Depends(get_session)) -> AlertCRUD:
    return AlertCRUD(session=session)


def decode_token(token: str, authenticate_value: Union[str, None] = None) -> Dict[str, str]:
    try:
        payload = jwt_decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except (ExpiredSignatureError, InvalidSignatureError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired.",
            headers={"WWW-Authenticate": authenticate_value} if authenticate_value else None,
        )
    except DecodeError:
        raise HTTPException(
            status_code=status.HTTP_406_NOT_ACCEPTABLE,
            detail="Invalid token.",
            headers={"WWW-Authenticate": authenticate_value} if authenticate_value else None,
        )
    return payload


def process_token(
    token: str, jwt_template: Type[JWTTemplate], authenticate_value: Union[str, None] = None
) -> JWTTemplate:
    payload = decode_token(token)
    # Verify the JWT template
    try:
        return jwt_template(**payload)
    except ValidationError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token payload.",
            headers={"WWW-Authenticate": authenticate_value} if authenticate_value else None,
        )


def get_jwt(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
) -> TokenPayload:
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
    jwt_payload = process_token(token, TokenPayload)
    if set(jwt_payload.scopes).isdisjoint(security_scopes.scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incompatible token scope.",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return jwt_payload


async def get_current_user(
    security_scopes: SecurityScopes,
    token: str = Depends(oauth2_scheme),
    users: UserCRUD = Depends(get_user_crud),
) -> User:
    """Dependency to use as fastapi.security.Security with scopes"""
    token_payload = get_jwt(security_scopes, token)
    return cast(User, await users.get(token_payload.sub, strict=True))


async def dispatch_webhook(url: str, payload: BaseModel) -> None:
    async with AsyncClient(timeout=5) as client:
        try:
            response = await client.post(url, json=payload.model_dump_json())
            response.raise_for_status()
            logger.info(f"Successfully dispatched to {url}")
        except HTTPStatusError as e:
            logger.error(f"Error dispatching webhook to {url}: {e.response.status_code} - {e.response.text}")
