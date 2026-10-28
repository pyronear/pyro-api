# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import logging
from typing import Any, Dict, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, SecurityScopes
from httpx import AsyncClient, HTTPStatusError
from jwt import ExpiredSignatureError, PyJWTError, get_unverified_header
from jwt import decode as jwt_decode
from pydantic import BaseModel, ValidationError
from sqlmodel.ext.asyncio.session import AsyncSession
from starlette.concurrency import run_in_threadpool

from app.core.config import settings
from app.core.keycloak import (
    KeycloakUnavailableError,
    decode_keycloak_token,
    introspect_keycloak_token,
    map_keycloak_roles,
)
from app.crud import AlertCRUD, CameraCRUD, DetectionCRUD, OrganizationCRUD, SequenceCRUD, UserCRUD, WebhookCRUD
from app.crud.crud_occlusion_mask import OcclusionMaskCRUD
from app.crud.crud_pose import PoseCRUD
from app.db import get_session
from app.models import Role
from app.schemas.login import TokenPayload

logger = logging.getLogger("uvicorn.error")

__all__ = ["get_user_crud"]

bearer_scheme = HTTPBearer(
    auto_error=False,
    description="Keycloak access token, or an API-issued camera token.",
)


def get_user_crud(session: AsyncSession = Depends(get_session)) -> UserCRUD:
    return UserCRUD(session=session)


def get_camera_crud(session: AsyncSession = Depends(get_session)) -> CameraCRUD:
    return CameraCRUD(session=session)


def get_pose_crud(session: AsyncSession = Depends(get_session)) -> PoseCRUD:
    return PoseCRUD(session=session)


def get_occlusion_mask_crud(session: AsyncSession = Depends(get_session)) -> OcclusionMaskCRUD:
    return OcclusionMaskCRUD(session=session)


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


def _unauthorized(detail: str, authenticate_value: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=detail,
        headers={"WWW-Authenticate": authenticate_value},
    )


async def _decode_keycloak(token: str, authenticate_value: str) -> TokenPayload:
    """Local checks first (signature, expiry, issuer, audience, claims), so bad tokens never reach Keycloak.
    Then introspection, so a revoked session or disabled user is rejected on its next request.
    """
    if settings.KEYCLOAK_ISSUER is None:
        raise _unauthorized("Invalid token.", authenticate_value)
    try:
        claims = await run_in_threadpool(decode_keycloak_token, token)
        try:
            token_payload = TokenPayload.model_validate({
                "sub": claims["sub"],
                "scopes": map_keycloak_roles(claims.get("roles")),
                "organization_id": claims.get("organization_id"),
                "auth_source": "keycloak",
            })
        except ValidationError:
            raise _unauthorized("Invalid token payload.", authenticate_value)
        if not await introspect_keycloak_token(token):
            raise _unauthorized("Token is no longer active.", authenticate_value)
    except KeycloakUnavailableError:
        logger.exception("Keycloak is unavailable")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service unavailable.",
        )
    return token_payload


def _decode_api(token: str, authenticate_value: str) -> TokenPayload:
    payload: Dict[str, Any] = jwt_decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    try:
        token_payload = TokenPayload.model_validate({**payload, "auth_source": "api"})
    except ValidationError:
        raise _unauthorized("Invalid token payload.", authenticate_value)
    if not token_payload.sub.isdigit() or int(token_payload.sub) <= 0:
        raise _unauthorized("Invalid token payload.", authenticate_value)
    if not settings.LEGACY_USER_TOKENS_ENABLED and token_payload.scopes != [Role.CAMERA]:
        raise _unauthorized("API-issued user tokens are disabled, sign in with Keycloak.", authenticate_value)
    return token_payload


async def process_token(token: str, authenticate_value: str = "Bearer") -> TokenPayload:
    """Verify a bearer token and normalize it, whichever issuer it comes from.

    The verification path is picked from the unverified `alg` header, and each path only accepts its own
    algorithm, so a token can't pick its own key (e.g. an HS256 token signed with the realm public key).
    """
    try:
        alg = get_unverified_header(token).get("alg")
        if alg == "RS256":
            return await _decode_keycloak(token, authenticate_value)
        if alg == settings.JWT_ALGORITHM:
            return _decode_api(token, authenticate_value)
    except ExpiredSignatureError:
        raise _unauthorized("Token has expired.", authenticate_value)
    except PyJWTError:
        raise _unauthorized("Invalid token.", authenticate_value)
    raise _unauthorized("Invalid token.", authenticate_value)


async def get_jwt(
    security_scopes: SecurityScopes,
    credentials: Union[HTTPAuthorizationCredentials, None] = Depends(bearer_scheme),
) -> TokenPayload:
    authenticate_value = f'Bearer scope="{security_scopes.scope_str}"' if security_scopes.scopes else "Bearer"
    if credentials is None:
        raise _unauthorized("Not authenticated", authenticate_value)
    jwt_payload = await process_token(credentials.credentials, authenticate_value)
    if set(jwt_payload.scopes).isdisjoint(security_scopes.scopes):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incompatible token scope.",
            headers={"WWW-Authenticate": authenticate_value},
        )
    return jwt_payload


async def dispatch_webhook(url: str, payload: BaseModel) -> None:
    async with AsyncClient(timeout=5) as client:
        try:
            response = await client.post(url, json=payload.model_dump_json())
            response.raise_for_status()
            logger.info(f"Successfully dispatched to {url}")
        except HTTPStatusError as e:
            logger.error(f"Error dispatching webhook to {url}: {e.response.status_code} - {e.response.text}")
