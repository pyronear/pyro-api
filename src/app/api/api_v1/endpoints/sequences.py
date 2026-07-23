# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from datetime import date, timedelta
from typing import Any, List, Union, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_alert_crud, get_camera_crud, get_detection_crud, get_jwt, get_sequence_crud
from app.core.time import utcnow
from app.crud import AlertCRUD, CameraCRUD, DetectionCRUD, SequenceCRUD
from app.db import get_session
from app.models import AlertSequence, AnnotationType, Camera, Detection, Sequence, UserRole
from app.schemas.alerts import AlertCreate
from app.schemas.detections import DetectionRead, DetectionSequence, DetectionWithUrl
from app.schemas.login import TokenPayload
from app.schemas.sequences import SequenceLabel, SequenceRead
from app.services.alerts import refresh_alert_state
from app.services.risk import FwiClass, risk_service
from app.services.sequence_confidence import max_conf_filter_clause
from app.services.sequence_counts import get_detection_counts_by_sequence_ids
from app.services.storage import s3_service
from app.services.telemetry import telemetry_client

router = APIRouter()


async def verify_org_rights(
    organization_id: int, camera_id: int, cameras: CameraCRUD = Depends(get_camera_crud)
) -> None:
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")


def _serialize_sequence(sequence: Sequence, detections_count: int = 0) -> SequenceRead:
    return SequenceRead(**sequence.model_dump(), detections_count=detections_count)


@router.get("/{sequence_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific sequence")
async def get_sequence(
    sequence_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> SequenceRead:
    telemetry_client.capture(token_payload.sub, event="sequences-get", properties={"sequence_id": sequence_id})
    sequence = cast(Sequence, await sequences.get(sequence_id, strict=True))

    if not token_payload.is_admin:
        await verify_org_rights(token_payload.organization_id, sequence.camera_id, cameras)

    counts = await get_detection_counts_by_sequence_ids(session, [sequence.id])
    return _serialize_sequence(sequence, counts.get(sequence.id, 0))


@router.get(
    "/{sequence_id}/detections", status_code=status.HTTP_200_OK, summary="Fetch the detections of a specific sequence"
)
async def fetch_sequence_detections(
    sequence_id: int = Path(..., gt=0),
    limit: int = Query(10, description="Maximum number of detections to fetch", ge=1, le=100),
    offset: int = Query(0, description="Number of detections to skip", ge=0),
    desc: bool = Query(True, description="Whether to order the detections by created_at in descending order"),
    with_crop: bool = Query(
        False,
        description="If true, presign and include crop_url for detections that have a crop. Defaults to false to skip the extra S3 head requests when crops are not needed.",
    ),
    cameras: CameraCRUD = Depends(get_camera_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[DetectionWithUrl]:
    telemetry_client.capture(token_payload.sub, event="sequences-get", properties={"sequence_id": sequence_id})
    sequence = cast(Sequence, await sequences.get(sequence_id, strict=True))
    camera = cast(Camera, await cameras.get(sequence.camera_id, strict=True))
    if not token_payload.is_admin and token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    # Get the bucket of the camera's organization
    bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(camera.organization_id))
    fetched = await detections.fetch_all(
        filters=("sequence_id", sequence_id),
        order_by="created_at",
        order_desc=desc,
        limit=limit,
        offset=offset,
    )
    return [
        DetectionWithUrl(
            **DetectionRead(**elt.model_dump()).model_dump(),
            url=bucket.get_public_url(elt.bucket_key, verify_exists=False),
            crop_url=(
                bucket.get_public_url(elt.crop_bucket_key, verify_exists=False)
                if with_crop and elt.crop_bucket_key
                else None
            ),
        )
        for elt in fetched
    ]


@router.get(
    "/unlabeled/latest",
    status_code=status.HTTP_200_OK,
    summary="Fetch all the unlabeled sequences from the last 24 hours",
)
async def fetch_latest_unlabeled_sequences(
    risk_score: Union[FwiClass, None] = Query(
        None,
        description="Override FWI class applied to every sequence; bypasses risk-api lookup. Ignored for admins.",
    ),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[SequenceRead]:
    telemetry_client.capture(token_payload.sub, event="sequence-fetch-latest")
    is_admin = token_payload.is_admin

    stmt: Any = (
        select(Sequence)
        .where(Sequence.started_at > utcnow() - timedelta(hours=24))
        .where(Sequence.is_wildfire.is_(None))  # type: ignore[union-attr]
    )
    # Admins see every organization's sequences without risk-score filtering
    if not is_admin:
        camera_ids = (
            await session.exec(select(Camera.id).where(Camera.organization_id == token_payload.organization_id))
        ).all()
        classes: dict[int, Union[str, None]] = (
            dict.fromkeys(camera_ids, risk_score) if risk_score is not None else dict(risk_service.scores())
        )
        stmt = stmt.where(Sequence.camera_id.in_(camera_ids))  # type: ignore[attr-defined]
        seq_filter = max_conf_filter_clause(classes)
        if seq_filter is not None:
            stmt = stmt.where(seq_filter)
    stmt = stmt.order_by(Sequence.started_at.desc()).limit(15)  # type: ignore[attr-defined]

    fetched_sequences = (await session.exec(stmt)).all()
    counts = await get_detection_counts_by_sequence_ids(session, [sequence.id for sequence in fetched_sequences])
    return [_serialize_sequence(sequence, counts.get(sequence.id, 0)) for sequence in fetched_sequences]


@router.get("/all/fromdate", status_code=status.HTTP_200_OK, summary="Fetch all the sequences for a specific date")
async def fetch_sequences_from_date(
    from_date: date = Query(),
    limit: Union[int, None] = Query(15, description="Maximum number of sequences to fetch"),
    offset: Union[int, None] = Query(0, description="Number of sequences to skip before starting to fetch"),
    risk_score: Union[FwiClass, None] = Query(
        None,
        description="Override FWI class applied to every sequence; bypasses risk-api lookup. Ignored for admins.",
    ),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[SequenceRead]:
    telemetry_client.capture(token_payload.sub, event="sequence-fetch-from-date")
    is_admin = token_payload.is_admin

    stmt: Any = select(Sequence).where(func.date(Sequence.started_at) == from_date)
    # Admins see every organization's sequences without risk-score filtering
    if not is_admin:
        # Limit to cameras in the same organization
        camera_ids = (
            await session.exec(select(Camera.id).where(Camera.organization_id == token_payload.organization_id))
        ).all()
        classes: dict[int, str | None]
        if risk_score is not None:
            classes = dict.fromkeys(camera_ids, risk_score)
        else:
            scores = await risk_service.get_scores_for_date(from_date, organization_id=token_payload.organization_id)
            classes = dict(scores)

        stmt = stmt.where(Sequence.camera_id.in_(camera_ids))  # type: ignore[attr-defined]
        seq_filter = max_conf_filter_clause(classes)
        if seq_filter is not None:
            stmt = stmt.where(seq_filter)
    stmt = stmt.order_by(Sequence.started_at.desc()).limit(limit).offset(offset)  # type: ignore[attr-defined]

    fetched_sequences = (await session.exec(stmt)).all()
    counts = await get_detection_counts_by_sequence_ids(session, [sequence.id for sequence in fetched_sequences])
    return [_serialize_sequence(sequence, counts.get(sequence.id, 0)) for sequence in fetched_sequences]


@router.delete("/{sequence_id}", status_code=status.HTTP_200_OK, summary="Delete a sequence")
async def delete_sequence(
    sequence_id: int = Path(..., gt=0),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    alerts: AlertCRUD = Depends(get_alert_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="sequence-deletion", properties={"sequence_id": sequence_id})
    alert_ids_res = await session.exec(select(AlertSequence.alert_id).where(AlertSequence.sequence_id == sequence_id))
    alert_ids = list(alert_ids_res.all())
    # Unset the sequence_id in the detections
    det_ids = await session.exec(select(Detection.id).where(Detection.sequence_id == sequence_id))
    for det_id in det_ids.all():
        await detections.update(det_id, DetectionSequence(sequence_id=None))
    # Drop alert links for this sequence to avoid FK issues
    delete_stmt: Any = delete(AlertSequence).where(cast(Any, AlertSequence.sequence_id) == sequence_id)
    await session.exec(delete_stmt)
    await session.commit()
    # Delete the sequence
    await sequences.delete(sequence_id)
    # Refresh affected alerts
    for aid in alert_ids:
        await refresh_alert_state(aid, session, alerts)


@router.patch("/{sequence_id}/label", status_code=status.HTTP_200_OK, summary="Label the nature of the sequence")
async def label_sequence(
    payload: SequenceLabel,
    sequence_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    alerts: AlertCRUD = Depends(get_alert_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> Sequence:
    telemetry_client.capture(token_payload.sub, event="sequence-label", properties={"sequence_id": sequence_id})
    sequence = cast(Sequence, await sequences.get(sequence_id, strict=True))

    if not token_payload.is_admin:
        await verify_org_rights(token_payload.organization_id, sequence.camera_id, cameras)

    updated = await sequences.update(sequence_id, payload)

    if payload.is_wildfire is None or payload.is_wildfire == AnnotationType.WILDFIRE_SMOKE:
        return updated

    alert_ids_res = await session.exec(select(AlertSequence.alert_id).where(AlertSequence.sequence_id == sequence_id))
    alert_ids = list(alert_ids_res.all())

    # If the sequence is the only one in all of its alerts, leave them as-is —
    # detaching and recreating would just churn the alert id for no benefit.
    if alert_ids:
        siblings_stmt: Any = (
            select(AlertSequence.sequence_id)
            .where(cast(Any, AlertSequence.alert_id).in_(alert_ids))
            .where(AlertSequence.sequence_id != sequence_id)
            .limit(1)
        )
        siblings_res = await session.exec(siblings_stmt)
        if siblings_res.first() is None:
            return updated

        delete_links: Any = delete(AlertSequence).where(cast(Any, AlertSequence.sequence_id) == sequence_id)
        await session.exec(delete_links)
        await session.commit()
        for aid in alert_ids:
            await refresh_alert_state(aid, session, alerts)

    # Create a fresh alert for this sequence alone
    camera = cast(Camera, await cameras.get(sequence.camera_id, strict=True))
    new_alert = await alerts.create(
        AlertCreate(
            organization_id=camera.organization_id,
            started_at=sequence.started_at,
            last_seen_at=sequence.last_seen_at,
            lat=None,
            lon=None,
        )
    )
    session.add(AlertSequence(alert_id=new_alert.id, sequence_id=sequence_id))
    await session.commit()

    return updated
