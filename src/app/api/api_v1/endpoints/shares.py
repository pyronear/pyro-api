# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import timedelta
from typing import Any, List, Tuple, Union, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, Security, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints.alerts import verify_org_rights
from app.api.dependencies import get_alert_crud, get_jwt, get_share_crud
from app.core.config import settings
from app.core.security import generate_share_token, hash_share_token
from app.core.time import utcnow
from app.crud import AlertCRUD, ShareCRUD
from app.db import get_session
from app.models import Alert, AlertShare, UserRole
from app.schemas.login import TokenPayload
from app.schemas.shares import (
    ShareCreate,
    ShareCreated,
    ShareCreation,
    SharedAlertRead,
    ShareRead,
    ShareRevocation,
    ShareStatus,
)
from app.services.shares import build_shared_alert, serialize_share, share_status
from app.services.telemetry import telemetry_client

router = APIRouter()


def verify_share_rights(token_payload: TokenPayload, share: AlertShare) -> None:
    if not token_payload.is_admin and token_payload.organization_id != share.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a public link to an alert")
async def create_share(
    payload: ShareCreate,
    alerts: AlertCRUD = Depends(get_alert_crud),
    shares: ShareCRUD = Depends(get_share_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> ShareCreated:
    telemetry_client.capture(token_payload.sub, event="shares-create", properties={"alert_id": payload.alert_id})
    alert = cast(Alert, await alerts.get(payload.alert_id, strict=True))
    if not token_payload.is_admin:
        verify_org_rights(token_payload.organization_id, alert)

    # Only the hash is stored: the token is returned once, here
    token = generate_share_token()
    share = await shares.create(
        ShareCreation(
            alert_id=alert.id,
            organization_id=alert.organization_id,
            created_by=token_payload.sub,
            token_hash=hash_share_token(token),
            expires_at=utcnow() + timedelta(hours=settings.SHARE_EXPIRE_HOURS),
        )
    )
    return ShareCreated(share_id=share.id, alert_id=share.alert_id, token=token, expires_at=share.expires_at)


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch the public links of my organization")
async def fetch_shares(
    alert_id: Union[int, None] = Query(None, gt=0, description="Only the links of this alert"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of links to fetch"),
    offset: int = Query(0, ge=0, description="Number of links to skip before starting to fetch"),
    shares: ShareCRUD = Depends(get_share_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[ShareRead]:
    telemetry_client.capture(token_payload.sub, event="shares-fetch")
    filters: List[Tuple[str, Any]] = []
    if not token_payload.is_admin:
        filters.append(("organization_id", token_payload.organization_id))
    if alert_id is not None:
        filters.append(("alert_id", alert_id))
    entries = await shares.fetch_all(
        filters=filters, order_by="created_at", order_desc=True, limit=limit, offset=offset
    )
    now = utcnow()
    return [serialize_share(share, now) for share in entries]


@router.delete("/{share_id}", status_code=status.HTTP_200_OK, summary="Cancel a public link")
async def revoke_share(
    share_id: int = Path(..., gt=0),
    shares: ShareCRUD = Depends(get_share_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> ShareRead:
    telemetry_client.capture(token_payload.sub, event="shares-revoke", properties={"share_id": share_id})
    share = cast(AlertShare, await shares.get(share_id, strict=True))
    verify_share_rights(token_payload, share)
    # Soft revoke: the row stays so the public route can tell a cancelled link from an unknown one
    if share.revoked_at is None:
        share = await shares.update(share_id, ShareRevocation(revoked_at=utcnow()))
    return serialize_share(share)


@router.get(
    "/public/{token}",
    status_code=status.HTTP_200_OK,
    summary="Fetch a shared alert from its public link, without an account",
)
async def get_shared_alert(
    response: Response,
    token: str = Path(..., min_length=1, max_length=128),
    shares: ShareCRUD = Depends(get_share_crud),
    alerts: AlertCRUD = Depends(get_alert_crud),
    session: AsyncSession = Depends(get_session),
) -> SharedAlertRead:
    share = await shares.get_by_token(token)
    if share is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link not found.")
    # The token itself never goes to telemetry
    telemetry_client.capture(f"share-{share.id}", event="shares-public-get", properties={"alert_id": share.alert_id})
    if share_status(share) != ShareStatus.ACTIVE:
        raise HTTPException(status_code=status.HTTP_410_GONE, detail="Share link expired.")

    alert = cast(Alert, await alerts.get(share.alert_id, strict=True))
    # A revoked or expired link must not be served from a cache
    response.headers["Cache-Control"] = "no-store"
    return await build_shared_alert(session, alert, share.expires_at)
