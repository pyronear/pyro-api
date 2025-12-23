# Copyright (C) 2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import date, datetime, timedelta
from typing import List, Union, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_alert_crud, get_jwt, get_sequence_crud
from app.crud import AlertCRUD, SequenceCRUD
from app.db import get_session
from app.models import Alert, AlertSequence, Sequence, UserRole
from app.schemas.login import TokenPayload
from app.services.telemetry import telemetry_client

router = APIRouter()


async def verify_org_rights(organization_id: int, alert: Alert) -> None:
    if organization_id != alert.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")


@router.get("/{alert_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific alert")
async def get_alert(
    alert_id: int = Path(..., gt=0),
    alerts: AlertCRUD = Depends(get_alert_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Alert:
    telemetry_client.capture(token_payload.sub, event="alerts-get", properties={"alert_id": alert_id})
    alert = cast(Alert, await alerts.get(alert_id, strict=True))

    if UserRole.ADMIN not in token_payload.scopes:
        await verify_org_rights(token_payload.organization_id, alert)

    return alert


@router.get(
    "/{alert_id}/sequences", status_code=status.HTTP_200_OK, summary="Fetch the sequences associated to an alert"
)
async def fetch_alert_sequences(
    alert_id: int = Path(..., gt=0),
    limit: int = Query(10, description="Maximum number of sequences to fetch", ge=1, le=100),
    desc: bool = Query(True, description="Whether to order the sequences by last_seen_at in descending order"),
    alerts: AlertCRUD = Depends(get_alert_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Sequence]:
    telemetry_client.capture(token_payload.sub, event="alerts-sequences-get", properties={"alert_id": alert_id})
    alert = cast(Alert, await alerts.get(alert_id, strict=True))
    if UserRole.ADMIN not in token_payload.scopes:
        await verify_org_rights(token_payload.organization_id, alert)

    stmt = (
        select(Sequence)
        .join(AlertSequence, AlertSequence.sequence_id == Sequence.id)
        .where(AlertSequence.alert_id == alert_id)
        .order_by(Sequence.last_seen_at.desc() if desc else Sequence.last_seen_at.asc())  # type: ignore[arg-type]
        .limit(limit)
    )
    res = await session.exec(stmt)
    return res.all()


@router.get(
    "/unlabeled/latest",
    status_code=status.HTTP_200_OK,
    summary="Fetch all the alerts with unlabeled sequences from the last 24 hours",
)
async def fetch_latest_unlabeled_alerts(
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Alert]:
    telemetry_client.capture(token_payload.sub, event="alerts-fetch-latest")

    alerts_stmt = (
        select(Alert)
        .join(AlertSequence, AlertSequence.alert_id == Alert.id)
        .join(Sequence, Sequence.id == AlertSequence.sequence_id)
        .where(Alert.organization_id == token_payload.organization_id)
        .where(Sequence.last_seen_at > datetime.utcnow() - timedelta(hours=24))
        .where(Sequence.is_wildfire.is_(None))  # type: ignore[union-attr]
        .order_by(Alert.started_at.desc())  # type: ignore[attr-defined]
        .limit(15)
    )
    alerts_res = await session.exec(alerts_stmt)
    return alerts_res.unique().all()  # unique to deduplicate joins


@router.get("/all/fromdate", status_code=status.HTTP_200_OK, summary="Fetch all the alerts for a specific date")
async def fetch_alerts_from_date(
    from_date: date = Query(),
    limit: Union[int, None] = Query(15, description="Maximum number of alerts to fetch"),
    offset: Union[int, None] = Query(0, description="Number of alerts to skip before starting to fetch"),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Alert]:
    telemetry_client.capture(token_payload.sub, event="alerts-fetch-from-date")

    alerts_stmt = (
        select(Alert)
        .where(Alert.organization_id == token_payload.organization_id)
        .where(func.date(Alert.started_at) == from_date)
        .order_by(Alert.started_at.desc())  # type: ignore[attr-defined]
        .limit(limit)
        .offset(offset)
    )
    alerts_res = await session.exec(alerts_stmt)
    return alerts_res.all()


@router.delete("/{alert_id}", status_code=status.HTTP_200_OK, summary="Delete an alert")
async def delete_alert(
    alert_id: int = Path(..., gt=0),
    alerts: AlertCRUD = Depends(get_alert_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="alert-deletion", properties={"alert_id": alert_id})

    # Ensure alert exists and org is valid
    alert = cast(Alert, await alerts.get(alert_id, strict=True))
    await verify_org_rights(token_payload.organization_id, alert)

    # Delete associations
    await session.exec(delete(AlertSequence).where(AlertSequence.alert_id == alert_id))
    await session.commit()
    # Delete alert
    await alerts.delete(alert_id)
