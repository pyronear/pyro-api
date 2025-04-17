# Copyright (C) 2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import date, datetime, timedelta
from operator import itemgetter
from typing import Dict, List, Tuple, Union, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Security, status
from sqlmodel import func, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_camera_crud, get_detection_crud, get_jwt, get_sequence_crud
from app.crud import CameraCRUD, DetectionCRUD, SequenceCRUD
from app.db import get_session
from app.models import Camera, Detection, Sequence, UserRole
from app.schemas.detections import DetectionSequence, DetectionWithUrl
from app.schemas.login import TokenPayload
from app.schemas.sequences import SequenceLabel, SequenceWithCone
from app.services.storage import s3_service
from app.services.telemetry import telemetry_client

router = APIRouter()


async def verify_org_rights(
    organization_id: int, camera_id: int, cameras: CameraCRUD = Depends(get_camera_crud)
) -> None:
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")


def _resolve_cone(azimuth: float, bboxes_str: str, aov: float) -> Tuple[float, float]:
    bboxes = ((xmin, xmax, conf) for xmin, _, xmax, _, conf in bboxes_str.strip("[]").split(","))  # type: ignore[misc,has-type]
    # Take the bbox with the highest confidence
    xmin, xmax, _ = max(bboxes, key=itemgetter(2))
    return azimuth + aov * ((xmin + xmax) / 2 - 0.5), aov * (xmax - xmin)


async def resolve_detection_cone(
    seq_ids: List[int], session: AsyncSession = Depends(get_session)
) -> Dict[int, Tuple[float, float]]:
    # Select the detections relevant to resolve the cone for each sequence
    # First get the minimum detection ID for each sequence
    min_det_ids = await session.exec(
        select(func.min(Detection.id).label("min_id"))
        .where(Detection.sequence_id.in_(seq_ids))  # type: ignore[union-attr]
        .group_by(Detection.sequence_id)
    )

    # Convert to a dictionary for lookup
    min_ids_dict = {seq_id: min_id for seq_id, min_id in min_det_ids.all()}

    # Now fetch the actual detection data with camera info
    det_infos = await session.exec(
        select(Detection.sequence_id, Detection.azimuth, Detection.bboxes, Camera.angle_of_view)
        .where(Detection.id.in_(min_ids_dict.values()))  # type: ignore[union-attr]
        .join(Camera, Detection.camera_id == Camera.id)  # type: ignore[arg-type]
    )
    # For each sequence, resolve the azimuth + opening angle
    return {seq_id: _resolve_cone(azimuth, bboxes_str, aov) for seq_id, azimuth, bboxes_str, aov in det_infos.all()}


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

    return sequence


@router.get(
    "/{sequence_id}/detections", status_code=status.HTTP_200_OK, summary="Fetch the detections of a specific sequence"
)
async def fetch_sequence_detections(
    sequence_id: int = Path(..., gt=0),
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
            **elt.__dict__,
            url=bucket.get_public_url(elt.bucket_key),
        )
        for elt in await detections.fetch_all(
            filters=("sequence_id", sequence_id),
            order_by="created_at",
            order_desc=True,
            limit=10,
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
) -> List[SequenceWithCone]:
    telemetry_client.capture(token_payload.sub, event="sequence-fetch-latest")
    # Limit to cameras in the same organization
    # Get camera IDs for org
    camera_ids = await session.exec(select(Camera.id).where(Camera.organization_id == token_payload.organization_id))

    # Get sequences for those cameras
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
    det_cones = await resolve_detection_cone([elt.__dict__["id"] for elt in fetched_sequences], session)
    return [
        SequenceWithCone(
            **elt.__dict__, cone_azimuth=det_cones[elt.__dict__["id"]][0], cone_angle=det_cones[elt.__dict__["id"]][1]
        )
        for elt in fetched_sequences
    ]


@router.get("/all/fromdate", status_code=status.HTTP_200_OK, summary="Fetch all the sequences for a specific date")
async def fetch_sequences_from_date(
    from_date: date = Query(),
    limit: Union[int, None] = Query(15, description="Maximum number of sequences to fetch"),
    offset: Union[int, None] = Query(0, description="Number of sequences to skip before starting to fetch"),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[SequenceWithCone]:
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
    det_cones = await resolve_detection_cone([elt.__dict__["id"] for elt in fetched_sequences], session)
    return [
        SequenceWithCone(
            **elt.__dict__, cone_azimuth=det_cones[elt.__dict__["id"]][0], cone_angle=det_cones[elt.__dict__["id"]][1]
        )
        for elt in fetched_sequences
    ]


@router.delete("/{sequence_id}", status_code=status.HTTP_200_OK, summary="Delete a sequence")
async def delete_sequence(
    sequence_id: int = Path(..., gt=0),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="sequence-deletion", properties={"sequence_id": sequence_id})
    # Unset the sequence_id in the detections
    det_ids = await session.exec(select(Detection.id).where(Detection.sequence_id == sequence_id))
    for det_id in det_ids.all():
        await detections.update(det_id, DetectionSequence(sequence_id=None))
    # Delete the sequence
    await sequences.delete(sequence_id)


@router.patch("/{sequence_id}/label", status_code=status.HTTP_200_OK, summary="Label the nature of the sequence")
async def label_sequence(
    payload: SequenceLabel,
    sequence_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> Sequence:
    telemetry_client.capture(token_payload.sub, event="sequence-label", properties={"sequence_id": sequence_id})
    sequence = cast(Sequence, await sequences.get(sequence_id, strict=True))

    if UserRole.ADMIN not in token_payload.scopes:
        await verify_org_rights(token_payload.organization_id, sequence.camera_id, cameras)

    return await sequences.update(sequence_id, payload)
