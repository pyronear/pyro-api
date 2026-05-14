# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


import csv
import io
from datetime import date, datetime, time, timedelta
from typing import Any, Dict, Iterable, Iterator, List, Union, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from fastapi.responses import StreamingResponse
from sqlalchemy import asc, desc
from sqlalchemy.sql import ColumnElement
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_alert_crud, get_camera_crud, get_jwt, get_sequence_crud
from app.core.time import utcnow
from app.crud import AlertCRUD, CameraCRUD, SequenceCRUD
from app.db import get_session
from app.models import Alert, AlertSequence, Camera, Sequence, UserRole
from app.schemas.alerts import AlertCreate, AlertReadWithSequences
from app.schemas.login import TokenPayload
from app.schemas.sequences import SequenceRead
from app.services.alerts import refresh_alert_state
from app.services.risk import FwiClass, risk_service
from app.services.sequence_confidence import max_conf_filter_clause
from app.services.sequence_counts import get_detection_counts_by_sequence_ids
from app.services.telemetry import telemetry_client

router = APIRouter()


def verify_org_rights(organization_id: int, alert: Alert) -> None:
    if organization_id != alert.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")


async def _fetch_sequences_by_alert_ids(
    session: AsyncSession,
    alert_ids: List[int],
    seq_filter: Union[ColumnElement[bool], None] = None,
) -> Dict[int, List[Sequence]]:
    mapping: Dict[int, List[Sequence]] = {}
    if not alert_ids:
        return mapping
    seq_stmt: Any = (
        select(AlertSequence.alert_id, Sequence)
        .join(Sequence, cast(Any, Sequence.id == AlertSequence.sequence_id))
        .where(AlertSequence.alert_id.in_(alert_ids))  # type: ignore[attr-defined]
    )
    if seq_filter is not None:
        seq_stmt = seq_stmt.where(seq_filter)
    seq_stmt = seq_stmt.order_by(cast(Any, AlertSequence.alert_id), desc(cast(Any, Sequence.last_seen_at)))
    res = await session.exec(seq_stmt)
    for alert_id, sequence in res.all():
        mapping.setdefault(int(alert_id), []).append(sequence)
    return mapping


async def _resolve_fwi_class_per_camera(
    session: AsyncSession,
    organization_id: int,
    target_date: Union[date, None] = None,
    override_class: Union[str, None] = None,
) -> Dict[int, Union[str, None]]:
    """Resolve ``{camera_id: fwi_class}`` for the org, picking override -> per-date -> today's cache."""
    if override_class is not None:
        cam_ids = (await session.exec(select(Camera.id).where(Camera.organization_id == organization_id))).all()
        return dict.fromkeys(cam_ids, override_class)
    if target_date is not None:
        scores = await risk_service.get_scores_for_date(target_date, organization_id=organization_id)
        return {cid: cls for cid, cls in scores.items()}
    return {cid: cls for cid, cls in risk_service.scores().items()}


def _serialize_sequence(sequence: Sequence, detections_count: int = 0) -> SequenceRead:
    return SequenceRead(**sequence.model_dump(), detections_count=detections_count)


def _serialize_alert(
    alert: Alert, sequences: List[Sequence], detection_counts: Dict[int, int]
) -> AlertReadWithSequences:
    return AlertReadWithSequences(
        **alert.model_dump(),
        sequences=[_serialize_sequence(sequence, detection_counts.get(sequence.id, 0)) for sequence in sequences],
    )


_ALERT_EXPORT_COLUMNS = ["id", "lat", "lon", "started_at", "last_seen_at"]


def _iter_alerts_csv(alerts: Iterable[Alert]) -> Iterator[str]:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(_ALERT_EXPORT_COLUMNS)
    yield buf.getvalue()
    buf.seek(0)
    buf.truncate(0)
    for a in alerts:
        writer.writerow([
            a.id,
            "" if a.lat is None else a.lat,
            "" if a.lon is None else a.lon,
            a.started_at.isoformat(),
            a.last_seen_at.isoformat(),
        ])
        yield buf.getvalue()
        buf.seek(0)
        buf.truncate(0)


def _build_alerts_csv_response(alerts: List[Alert], from_date: date, to_date: date) -> StreamingResponse:
    filename = f"alerts_{from_date.isoformat()}_{to_date.isoformat()}.csv"
    headers = {"Content-Disposition": f'attachment; filename="{filename}"'}
    return StreamingResponse(_iter_alerts_csv(alerts), media_type="text/csv", headers=headers)


@router.get(
    "/export",
    status_code=status.HTTP_200_OK,
    summary="Export alerts in a date range as CSV",
    response_class=StreamingResponse,
)
async def export_alerts_csv(
    from_date: date = Query(..., description="Inclusive lower bound on started_at (UTC date)"),
    to_date: date = Query(..., description="Inclusive upper bound on started_at (UTC date)"),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> StreamingResponse:
    telemetry_client.capture(
        token_payload.sub,
        event="alerts-export",
        properties={"from_date": from_date.isoformat(), "to_date": to_date.isoformat()},
    )

    if to_date < from_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="to_date must be on or after from_date",
        )

    # DB columns store naive UTC datetimes (see app.core.time.utcnow), so we drop tzinfo here.
    start_dt = datetime.combine(from_date, time.min)
    end_dt = datetime.combine(to_date, time.max)

    stmt: Any = (
        select(Alert)
        .where(Alert.organization_id == token_payload.organization_id)
        .where(Alert.started_at >= start_dt)
        .where(Alert.started_at <= end_dt)
        .order_by(Alert.started_at.asc())  # type: ignore[attr-defined]
    )
    return _build_alerts_csv_response(list((await session.exec(stmt)).all()), from_date, to_date)


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
    limit: Union[int, None] = Query(15, ge=1, description="Maximum number of alerts to fetch"),
    offset: Union[int, None] = Query(0, description="Number of alerts to skip before starting to fetch"),
    risk_score: Union[FwiClass, None] = Query(
        None, description="Override FWI class applied to every sequence; bypasses risk-api lookup."
    ),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[AlertReadWithSequences]:
    telemetry_client.capture(token_payload.sub, event="alerts-fetch-latest")

    fwi_classes_by_camera = await _resolve_fwi_class_per_camera(
        session, token_payload.organization_id, override_class=risk_score
    )
    seq_filter = max_conf_filter_clause(fwi_classes_by_camera)

    seq_match: Any = cast(
        Any,
        select(AlertSequence.alert_id).join(Sequence, cast(Any, Sequence.id == AlertSequence.sequence_id)),
    )
    seq_match = (
        seq_match.where(Sequence.last_seen_at > utcnow() - timedelta(hours=24)).where(Sequence.is_wildfire.is_(None))  # type: ignore[union-attr]
    )
    if seq_filter is not None:
        seq_match = seq_match.where(seq_filter)

    alerts_stmt: Any = (
        select(Alert)
        .where(Alert.organization_id == token_payload.organization_id)
        .where(cast(Any, Alert.id).in_(seq_match))
        .order_by(Alert.started_at.desc())  # type: ignore[attr-defined]
        .limit(limit)
        .offset(offset)
    )
    alerts = list((await session.exec(alerts_stmt)).all())
    alert_ids = [alert.id for alert in alerts]
    seq_map = await _fetch_sequences_by_alert_ids(session, alert_ids, seq_filter)
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

    fwi_classes_by_camera = await _resolve_fwi_class_per_camera(
        session, token_payload.organization_id, target_date=from_date, override_class=risk_score
    )
    seq_filter = max_conf_filter_clause(fwi_classes_by_camera)

    alerts_stmt: Any = (
        select(Alert)
        .where(Alert.organization_id == token_payload.organization_id)
        .where(func.date(Alert.started_at) == from_date)
    )
    if seq_filter is not None:
        seq_match: Any = select(AlertSequence.alert_id).join(
            Sequence, cast(Any, Sequence.id == AlertSequence.sequence_id)
        )
        seq_match = seq_match.where(seq_filter)
        alerts_stmt = alerts_stmt.where(cast(Any, Alert.id).in_(seq_match))
    alerts_stmt = alerts_stmt.order_by(Alert.started_at.desc()).limit(limit).offset(offset)  # type: ignore[attr-defined]

    alerts = list((await session.exec(alerts_stmt)).all())
    alert_ids = [alert.id for alert in alerts]
    seq_map = await _fetch_sequences_by_alert_ids(session, alert_ids, seq_filter)
    detection_counts = await get_detection_counts_by_sequence_ids(
        session,
        list({sequence.id for sequences in seq_map.values() for sequence in sequences}),
    )
    return [_serialize_alert(alert, seq_map.get(alert.id, []), detection_counts) for alert in alerts]


@router.post(
    "/{alert_id}/sequences/{sequence_id}/unmatch",
    status_code=status.HTTP_200_OK,
    summary="Detach a sequence from an alert; create a fresh alert if the sequence becomes orphaned",
)
async def unmatch_alert_sequence(
    alert_id: int = Path(..., gt=0),
    sequence_id: int = Path(..., gt=0),
    alerts: AlertCRUD = Depends(get_alert_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> Union[AlertReadWithSequences, None]:
    telemetry_client.capture(
        token_payload.sub,
        event="alerts-sequence-unmatch",
        properties={"alert_id": alert_id, "sequence_id": sequence_id},
    )
    alert = cast(Alert, await alerts.get(alert_id, strict=True))
    if UserRole.ADMIN not in token_payload.scopes:
        verify_org_rights(token_payload.organization_id, alert)

    link_stmt: Any = select(AlertSequence).where(
        AlertSequence.alert_id == alert_id, AlertSequence.sequence_id == sequence_id
    )
    link = (await session.exec(link_stmt)).first()
    if link is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Sequence is not attached to this alert.")

    count_stmt: Any = select(func.count()).select_from(AlertSequence).where(AlertSequence.alert_id == alert_id)
    sequence_count = int((await session.exec(count_stmt)).one())
    if sequence_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot unmatch the only sequence of an alert.",
        )

    delete_stmt: Any = (
        delete(AlertSequence)
        .where(cast(Any, AlertSequence.alert_id) == alert_id)
        .where(cast(Any, AlertSequence.sequence_id) == sequence_id)
    )
    await session.exec(delete_stmt)
    await session.commit()

    await refresh_alert_state(alert_id, session, alerts)

    other_links_stmt: Any = (
        select(func.count()).select_from(AlertSequence).where(AlertSequence.sequence_id == sequence_id)
    )
    other_links = int((await session.exec(other_links_stmt)).one())
    if other_links > 0:
        return None

    sequence = cast(Sequence, await sequences.get(sequence_id, strict=True))
    camera = cast(Camera, await cameras.get(sequence.camera_id, strict=True))
    if camera.organization_id != alert.organization_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Sequence camera does not belong to the same organization as the alert.",
        )
    new_alert = await alerts.create(
        AlertCreate(
            organization_id=alert.organization_id,
            started_at=sequence.started_at,
            last_seen_at=sequence.last_seen_at,
            lat=None,
            lon=None,
        )
    )
    session.add(AlertSequence(alert_id=new_alert.id, sequence_id=sequence_id))
    await session.commit()
    await session.refresh(new_alert)
    detection_counts = await get_detection_counts_by_sequence_ids(session, [sequence.id])
    return _serialize_alert(new_alert, [sequence], detection_counts)


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
