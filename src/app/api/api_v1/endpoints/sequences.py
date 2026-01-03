# Copyright (C) 2025-2026-2026-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from datetime import date, datetime, timedelta
from typing import Any, List, Union, cast

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from sqlmodel import delete, func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_alert_crud, get_camera_crud, get_detection_crud, get_jwt, get_sequence_crud
from app.crud import AlertCRUD, CameraCRUD, DetectionCRUD, SequenceCRUD
from app.db import get_session
from app.models import AlertSequence, AnnotationType, Camera, Detection, Sequence, UserRole
from app.schemas.alerts import AlertCreate, AlertUpdate
from app.schemas.detections import DetectionRead, DetectionSequence, DetectionWithUrl
from app.schemas.login import TokenPayload
from app.schemas.sequences import SequenceLabel, SequenceRead
from app.services.overlap import compute_overlap
from app.services.storage import s3_service
from app.services.telemetry import telemetry_client

router = APIRouter()


async def verify_org_rights(
    organization_id: int, camera_id: int, cameras: CameraCRUD = Depends(get_camera_crud)
) -> None:
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")


async def _refresh_alert_state(alert_id: int, session: AsyncSession, alerts: AlertCRUD) -> None:
    remaining_stmt: Any = (
        select(Sequence, Camera)
        .join(AlertSequence, cast(Any, AlertSequence.sequence_id) == Sequence.id)
        .join(Camera, cast(Any, Camera.id) == Sequence.camera_id)
    )
    remaining_stmt = remaining_stmt.where(AlertSequence.alert_id == alert_id)
    remaining_res = await session.exec(remaining_stmt)
    rows = remaining_res.all()
    if not rows:
        await alerts.delete(alert_id)
        return

    seqs = [row[0] for row in rows]
    cams = [row[1] for row in rows]
    new_start = min(seq.started_at for seq in seqs)
    new_last = max(seq.last_seen_at for seq in seqs)

    loc: Union[tuple[float, float], None] = None
    if len(rows) >= 2:
        records = []
        for seq, cam in zip(seqs, cams, strict=False):
            records.append({
                "id": seq.id,
                "lat": cam.lat,
                "lon": cam.lon,
                "sequence_azimuth": seq.sequence_azimuth,
                "cone_angle": seq.cone_angle,
                "is_wildfire": seq.is_wildfire,
                "started_at": seq.started_at,
                "last_seen_at": seq.last_seen_at,
            })
        df = compute_overlap(pd.DataFrame.from_records(records))
        loc = next((loc for locs in df["event_smoke_locations"].tolist() for loc in locs if loc is not None), None)

    await alerts.update(
        alert_id,
        AlertUpdate(
            started_at=new_start,
            last_seen_at=new_last,
            lat=loc[0] if loc else None,
            lon=loc[1] if loc else None,
        ),
    )


@router.get("/{sequence_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific sequence")
async def get_sequence(
    sequence_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Sequence:
    telemetry_client.capture(token_payload.sub, event="sequences-get", properties={"sequence_id": sequence_id})
    sequence = cast(Sequence, await sequences.get(sequence_id, strict=True))

    if UserRole.ADMIN not in token_payload.scopes:
        await verify_org_rights(token_payload.organization_id, sequence.camera_id, cameras)

    return SequenceRead(**sequence.model_dump())


@router.get(
    "/{sequence_id}/detections", status_code=status.HTTP_200_OK, summary="Fetch the detections of a specific sequence"
)
async def fetch_sequence_detections(
    sequence_id: int = Path(..., gt=0),
    limit: int = Query(10, description="Maximum number of detections to fetch", ge=1, le=100),
    desc: bool = Query(True, description="Whether to order the detections by created_at in descending order"),
    cameras: CameraCRUD = Depends(get_camera_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[DetectionWithUrl]:
    telemetry_client.capture(token_payload.sub, event="sequences-get", properties={"sequence_id": sequence_id})
    sequence = cast(Sequence, await sequences.get(sequence_id, strict=True))
    camera = cast(Camera, await cameras.get(sequence.camera_id, strict=True))
    if UserRole.ADMIN not in token_payload.scopes and token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    # Get the bucket of the camera's organization
    bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(camera.organization_id))
    return [
        DetectionWithUrl(
            **DetectionRead(**elt.model_dump()).model_dump(),
            url=bucket.get_public_url(elt.bucket_key),
        )
        for elt in await detections.fetch_all(
            filters=("sequence_id", sequence_id),
            order_by="created_at",
            order_desc=desc,
            limit=limit,
        )
    ]


@router.get(
    "/unlabeled/latest",
    status_code=status.HTTP_200_OK,
    summary="Fetch all the unlabeled sequences from the last 24 hours",
)
async def fetch_latest_unlabeled_sequences(
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[SequenceRead]:
    telemetry_client.capture(token_payload.sub, event="sequence-fetch-latest")
    camera_ids = await session.exec(select(Camera.id).where(Camera.organization_id == token_payload.organization_id))

    fetched_sequences = (
        await session.exec(
            select(Sequence)
            .where(Sequence.started_at > datetime.utcnow() - timedelta(hours=24))
            .where(Sequence.camera_id.in_(camera_ids.all()))  # type: ignore[attr-defined]
            .where(Sequence.is_wildfire.is_(None))  # type: ignore[union-attr]
            .order_by(Sequence.started_at.desc())  # type: ignore[attr-defined]
            .limit(15)
        )
    ).all()
    return [SequenceRead(**elt.model_dump()) for elt in fetched_sequences]


@router.get("/all/fromdate", status_code=status.HTTP_200_OK, summary="Fetch all the sequences for a specific date")
async def fetch_sequences_from_date(
    from_date: date = Query(),
    limit: Union[int, None] = Query(15, description="Maximum number of sequences to fetch"),
    offset: Union[int, None] = Query(0, description="Number of sequences to skip before starting to fetch"),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[SequenceRead]:
    telemetry_client.capture(token_payload.sub, event="sequence-fetch-from-date")
    # Limit to cameras in the same organization
    camera_ids = await session.exec(select(Camera.id).where(Camera.organization_id == token_payload.organization_id))
    # Identify the sequences from that day
    fetched_sequences = (
        await session.exec(
            select(Sequence)
            .where(func.date(Sequence.started_at) == from_date)
            .where(Sequence.camera_id.in_(camera_ids.all()))  # type: ignore[attr-defined]
            .order_by(Sequence.started_at.desc())  # type: ignore[attr-defined]
            .limit(limit)
            .offset(offset)
        )
    ).all()
    return [SequenceRead(**elt.model_dump()) for elt in fetched_sequences]


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
        await _refresh_alert_state(aid, session, alerts)


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

    if UserRole.ADMIN not in token_payload.scopes:
        await verify_org_rights(token_payload.organization_id, sequence.camera_id, cameras)

    updated = await sequences.update(sequence_id, payload)

    # If sequence is labeled as non-wildfire, remove it from alerts and refresh those alerts
    if payload.is_wildfire is not None and payload.is_wildfire != AnnotationType.WILDFIRE_SMOKE:
        alert_ids_res = await session.exec(
            select(AlertSequence.alert_id).where(AlertSequence.sequence_id == sequence_id)
        )
        alert_ids = list(alert_ids_res.all())
        if alert_ids:
            delete_links: Any = delete(AlertSequence).where(cast(Any, AlertSequence.sequence_id) == sequence_id)
            await session.exec(delete_links)
            await session.commit()
            for aid in alert_ids:
                await _refresh_alert_state(aid, session, alerts)
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
