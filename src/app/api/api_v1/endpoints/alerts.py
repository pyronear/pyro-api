# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from datetime import date, timedelta
from typing import Any, Dict, List, Literal, Union, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from sqlalchemy import asc, desc
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_alert_crud, get_jwt
from app.core.time import utcnow
from app.crud import AlertCRUD
from app.db import get_session
from app.models import Alert, AlertSequence, Sequence, UserRole
from app.schemas.alerts import AlertReadWithSequences
from app.schemas.login import TokenPayload
from app.schemas.sequences import SequenceRead
from app.services.risk import risk_service
from app.services.sequence_confidence import filter_by_class_per_camera
from app.services.sequence_counts import get_detection_counts_by_sequence_ids
from app.services.telemetry import telemetry_client

# FWI classes accepted as a manual ``risk_score`` override on the listing endpoints.
FwiClass = Literal["very_low", "low", "moderate", "high", "very_high", "extreme"]


router = APIRouter()


def verify_org_rights(organization_id: int, alert: Alert) -> None:
    if organization_id != alert.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")


async def _fetch_sequences_by_alert_ids(session: AsyncSession, alert_ids: List[int]) -> Dict[int, List[Sequence]]:
    mapping: Dict[int, List[Sequence]] = {}
    if not alert_ids:
        return mapping
    seq_stmt: Any = (
        select(AlertSequence.alert_id, Sequence)
        .join(Sequence, cast(Any, Sequence.id == AlertSequence.sequence_id))
        .where(AlertSequence.alert_id.in_(alert_ids))  # type: ignore[attr-defined]
        .order_by(cast(Any, AlertSequence.alert_id), desc(cast(Any, Sequence.last_seen_at)))
    )
    res = await session.exec(seq_stmt)
    for alert_id, sequence in res.all():
        mapping.setdefault(int(alert_id), []).append(sequence)
    return mapping


async def _apply_risk_filter_to_alerts(
    alerts: List[Alert],
    seq_map: Dict[int, List[Sequence]],
    target_date: Union[date, None] = None,
    organization_id: Union[int, None] = None,
    override_class: Union[str, None] = None,
) -> List[Alert]:
    """Drop sequences below the risk threshold and alerts that end up empty.

    Resolution priority for the per-camera FWI class:
    ``override_class`` (single value applied to all cameras) → risk-api ``/scores/{date}``
    when ``target_date`` is set → today's RAM cache.
    """
    all_seqs = [seq for seqs in seq_map.values() for seq in seqs]
    if override_class is not None:
        class_per_camera: Dict[int, Union[str, None]] = {seq.camera_id: override_class for seq in all_seqs}
    elif target_date is not None:
        scores = await risk_service.get_scores_for_date(target_date, organization_id=organization_id)
        class_per_camera = {seq.camera_id: scores.get(seq.camera_id) for seq in all_seqs}
    else:
        class_per_camera = {seq.camera_id: risk_service.class_for_camera(seq.camera_id) for seq in all_seqs}

    kept_ids = {seq.id for seq in filter_by_class_per_camera(all_seqs, class_per_camera)}
    kept_alerts: List[Alert] = []
    for alert in alerts:
        filtered = [seq for seq in seq_map.get(alert.id, []) if seq.id in kept_ids]
        if filtered:
            seq_map[alert.id] = filtered
            kept_alerts.append(alert)
    return kept_alerts


def _serialize_sequence(sequence: Sequence, detections_count: int = 0) -> SequenceRead:
    return SequenceRead(**sequence.model_dump(), detections_count=detections_count)


def _serialize_alert(
    alert: Alert, sequences: List[Sequence], detection_counts: Dict[int, int]
) -> AlertReadWithSequences:
    return AlertReadWithSequences(
        **alert.model_dump(),
        sequences=[_serialize_sequence(sequence, detection_counts.get(sequence.id, 0)) for sequence in sequences],
    )


@router.get("/{alert_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific alert")
async def get_alert(
    alert_id: int = Path(..., gt=0),
    alerts: AlertCRUD = Depends(get_alert_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> AlertReadWithSequences:
    telemetry_client.capture(token_payload.sub, event="alerts-get", properties={"alert_id": alert_id})
    alert = cast(Alert, await alerts.get(alert_id, strict=True))

    if UserRole.ADMIN not in token_payload.scopes:
        verify_org_rights(token_payload.organization_id, alert)

    seq_map = await _fetch_sequences_by_alert_ids(session, [alert.id])
    detection_counts = await get_detection_counts_by_sequence_ids(
        session, [sequence.id for sequence in seq_map.get(alert.id, [])]
    )
    return _serialize_alert(alert, seq_map.get(alert.id, []), detection_counts)


@router.get(
    "/{alert_id}/sequences", status_code=status.HTTP_200_OK, summary="Fetch the sequences associated to an alert"
)
async def fetch_alert_sequences(
    alert_id: int = Path(..., gt=0),
    limit: int = Query(10, description="Maximum number of sequences to fetch", ge=1, le=100),
    order_desc: bool = Query(True, description="Whether to order the sequences by last_seen_at in descending order"),
    alerts: AlertCRUD = Depends(get_alert_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[SequenceRead]:
    telemetry_client.capture(token_payload.sub, event="alerts-sequences-get", properties={"alert_id": alert_id})
    alert = cast(Alert, await alerts.get(alert_id, strict=True))
    if UserRole.ADMIN not in token_payload.scopes:
        verify_org_rights(token_payload.organization_id, alert)

    order_clause: Any = desc(cast(Any, Sequence.last_seen_at)) if order_desc else asc(cast(Any, Sequence.last_seen_at))

    seq_stmt: Any = select(Sequence).join(AlertSequence, cast(Any, AlertSequence.sequence_id == Sequence.id))
    seq_stmt = seq_stmt.where(AlertSequence.alert_id == alert_id).order_by(order_clause).limit(limit)

    res = await session.exec(seq_stmt)
    sequences = list(res.all())
    detection_counts = await get_detection_counts_by_sequence_ids(session, [sequence.id for sequence in sequences])
    return [_serialize_sequence(sequence, detection_counts.get(sequence.id, 0)) for sequence in sequences]


@router.get(
    "/unlabeled/latest",
    status_code=status.HTTP_200_OK,
    summary="Fetch all the alerts with unlabeled sequences from the last 24 hours",
)
async def fetch_latest_unlabeled_alerts(
    risk_score: Union[FwiClass, None] = Query(
        None, description="Override FWI class applied to every sequence; bypasses risk-api lookup."
    ),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[AlertReadWithSequences]:
    telemetry_client.capture(token_payload.sub, event="alerts-fetch-latest")

    alerts_stmt: Any = select(Alert).join(AlertSequence, cast(Any, AlertSequence.alert_id == Alert.id))
    alerts_stmt = alerts_stmt.join(Sequence, cast(Any, Sequence.id == AlertSequence.sequence_id))
    alerts_stmt = (
        alerts_stmt.where(Alert.organization_id == token_payload.organization_id)
        .where(Sequence.last_seen_at > utcnow() - timedelta(hours=24))
        .where(Sequence.is_wildfire.is_(None))  # type: ignore[union-attr]
        .order_by(Alert.started_at.desc())  # type: ignore[attr-defined]
        .limit(15)
    )
    alerts_res = await session.exec(alerts_stmt)
    alerts = list(alerts_res.unique().all())
    alert_ids = [alert.id for alert in alerts]
    seq_map = await _fetch_sequences_by_alert_ids(session, alert_ids)
    alerts = await _apply_risk_filter_to_alerts(alerts, seq_map, override_class=risk_score)
    detection_counts = await get_detection_counts_by_sequence_ids(
        session,
        list({sequence.id for sequences in seq_map.values() for sequence in sequences}),
    )
    return [_serialize_alert(alert, seq_map.get(alert.id, []), detection_counts) for alert in alerts]


@router.get("/all/fromdate", status_code=status.HTTP_200_OK, summary="Fetch all the alerts for a specific date")
async def fetch_alerts_from_date(
    from_date: date = Query(),
    limit: Union[int, None] = Query(15, description="Maximum number of alerts to fetch"),
    offset: Union[int, None] = Query(0, description="Number of alerts to skip before starting to fetch"),
    risk_score: Union[FwiClass, None] = Query(
        None, description="Override FWI class applied to every sequence; bypasses risk-api lookup."
    ),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[AlertReadWithSequences]:
    telemetry_client.capture(token_payload.sub, event="alerts-fetch-from-date")

    alerts_stmt: Any = (
        select(Alert)
        .where(Alert.organization_id == token_payload.organization_id)
        .where(func.date(Alert.started_at) == from_date)
        .order_by(Alert.started_at.desc())  # type: ignore[attr-defined]
        .limit(limit)
        .offset(offset)
    )
    alerts_res = await session.exec(alerts_stmt)
    alerts = list(alerts_res.all())
    alert_ids = [alert.id for alert in alerts]
    seq_map = await _fetch_sequences_by_alert_ids(session, alert_ids)
    alerts = await _apply_risk_filter_to_alerts(
        alerts,
        seq_map,
        target_date=from_date,
        organization_id=token_payload.organization_id,
        override_class=risk_score,
    )
    detection_counts = await get_detection_counts_by_sequence_ids(
        session,
        list({sequence.id for sequences in seq_map.values() for sequence in sequences}),
    )
    return [_serialize_alert(alert, seq_map.get(alert.id, []), detection_counts) for alert in alerts]


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
    verify_org_rights(token_payload.organization_id, alert)

    # Delete associations
    delete_stmt: Any = delete(AlertSequence).where(AlertSequence.alert_id == cast(Any, alert_id))
    await session.exec(delete_stmt)
    await session.commit()
    # Delete alert
    await alerts.delete(alert_id)
