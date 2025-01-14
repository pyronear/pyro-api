# Copyright (C) 2024-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime, timedelta
from typing import List, Optional, cast

from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Query,
    Security,
    UploadFile,
    status,
)
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import (
    dispatch_webhook,
    get_camera_crud,
    get_detection_crud,
    get_jwt,
    get_organization_crud,
    get_sequence_crud,
    get_webhook_crud,
)
from app.core.config import settings
from app.crud import CameraCRUD, DetectionCRUD, OrganizationCRUD, SequenceCRUD, WebhookCRUD
from app.db import get_session
from app.models import Camera, Detection, Organization, Role, Sequence, UserRole
from app.schemas.detections import (
    BOXES_PATTERN,
    COMPILED_BOXES_PATTERN,
    DetectionCreate,
    DetectionLabel,
    DetectionUrl,
    DetectionWithUrl,
)
from app.schemas.login import TokenPayload
from app.schemas.sequences import SequenceUpdate
from app.services.storage import s3_service, upload_file
from app.services.telegram import telegram_client
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new wildfire detection")
async def create_detection(
    background_tasks: BackgroundTasks,
    bboxes: str = Form(
        ...,
        description="string representation of list of detection localizations, each represented as a tuple of relative coords (max 3 decimals) in order: xmin, ymin, xmax, ymax, conf",
        pattern=BOXES_PATTERN,
        min_length=2,
        max_length=settings.MAX_BBOX_STR_LENGTH,
    ),
    azimuth: float = Form(..., gt=0, lt=360, description="angle between north and direction in degrees"),
    file: UploadFile = File(..., alias="file"),
    detections: DetectionCRUD = Depends(get_detection_crud),
    webhooks: WebhookCRUD = Depends(get_webhook_crud),
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> Detection:
    telemetry_client.capture(f"camera|{token_payload.sub}", event="detections-create")

    # Throw an error if the format is invalid and can't be captured by the regex
    if any(box[0] >= box[2] or box[1] >= box[3] for box in COMPILED_BOXES_PATTERN.findall(bboxes)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="xmin & ymin are expected to be respectively smaller than xmax & ymax",
        )

    # Upload media
    bucket_key = await upload_file(file, token_payload.organization_id, token_payload.sub)
    det = await detections.create(
        DetectionCreate(camera_id=token_payload.sub, bucket_key=bucket_key, azimuth=azimuth, bboxes=bboxes)
    )
    # Sequence handling
    # Check if there is a sequence that was seen recently
    sequence = await sequences.fetch_all(
        filters=[("camera_id", token_payload.sub), ("azimuth", det.azimuth)],
        inequality_pair=(
            "last_seen_at",
            ">",
            datetime.utcnow() - timedelta(seconds=settings.SEQUENCE_RELAXATION_SECONDS),
        ),
        order_by="last_seen_at",
        order_desc=True,
        limit=1,
    )
    if len(sequence) == 1:
        # Add detection to existing sequence
        await sequences.update(sequence[0].id, SequenceUpdate(last_seen_at=det.created_at))
    else:
        # Check if we've reached the threshold of detections per interval
        dets_ = await detections.fetch_all(
            filters=[("camera_id", token_payload.sub), ("azimuth", det.azimuth)],
            inequality_pair=(
                "created_at",
                ">",
                datetime.utcnow() - timedelta(seconds=settings.SEQUENCE_MIN_INTERVAL_SECONDS),
            ),
            order_by="created_at",
            order_desc=False,
            limit=settings.SEQUENCE_MIN_INTERVAL_DETS,
        )
        if len(dets_) >= settings.SEQUENCE_MIN_INTERVAL_DETS:
            # Create new sequence
            await sequences.create(
                Sequence(
                    camera_id=token_payload.sub,
                    azimuth=det.azimuth,
                    started_at=dets_[0].created_at,
                    last_seen_at=det.created_at,
                )
            )

    # Webhooks
    whs = await webhooks.fetch_all()
    if any(whs):
        for webhook in await webhooks.fetch_all():
            background_tasks.add_task(dispatch_webhook, webhook.url, det)
    # Telegram notifications
    if telegram_client.is_enabled:
        org = cast(Organization, await organizations.get(token_payload.organization_id, strict=True))
        if org.telegram_id:
            background_tasks.add_task(telegram_client.notify, org.telegram_id, det.model_dump_json())
    return det


@router.get("/{detection_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific detection")
async def get_detection(
    detection_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Detection:
    telemetry_client.capture(token_payload.sub, event="detections-get", properties={"detection_id": detection_id})
    detection = cast(Detection, await detections.get(detection_id, strict=True))

    if UserRole.ADMIN in token_payload.scopes:
        return detection

    camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return detection


@router.get("/{detection_id}/url", status_code=200)
async def get_detection_url(
    detection_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> DetectionUrl:
    """Resolve the temporary media image URL"""
    telemetry_client.capture(token_payload.sub, event="detections-url", properties={"detection_id": detection_id})
    # Check in DB
    detection = cast(Detection, await detections.get(detection_id, strict=True))

    if UserRole.ADMIN in token_payload.scopes:
        camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
        bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(camera.organization_id))
        return DetectionUrl(url=bucket.get_public_url(detection.bucket_key))

    camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    # Check in bucket
    bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(camera.organization_id))
    return DetectionUrl(url=bucket.get_public_url(detection.bucket_key))


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the detections")
async def fetch_detections(
    detections: DetectionCRUD = Depends(get_detection_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[Detection]:
    telemetry_client.capture(token_payload.sub, event="detections-fetch")
    if UserRole.ADMIN in token_payload.scopes:
        return [elt for elt in await detections.fetch_all()]

    cameras_list = await cameras.fetch_all(filters=("organization_id", token_payload.organization_id))
    camera_ids = [camera.id for camera in cameras_list]

    return await detections.fetch_all(in_pair=("camera_id", camera_ids))


@router.get("/unlabeled/fromdate", status_code=status.HTTP_200_OK, summary="Fetch all the unlabeled detections")
async def fetch_unlabeled_detections(
    from_date: datetime = Query(),
    limit: Optional[int] = Query(15, description="Maximum number of detections to fetch"),
    offset: Optional[int] = Query(0, description="Number of detections to skip before starting to fetch"),
    session: AsyncSession = Depends(get_session),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[DetectionWithUrl]:
    telemetry_client.capture(token_payload.sub, event="detections-fetch-unlabeled")

    if UserRole.ADMIN in token_payload.scopes:
        # Custom SQL query to fetch detections along with corresponding organization_id
        query = await session.exec(
            select(Detection, Camera.organization_id)  # type: ignore[attr-defined]
            .join(Camera, Detection.camera_id == Camera.id)  # type: ignore[arg-type]
            .where(Detection.is_wildfire.is_(None))  # type: ignore[union-attr]
            .where(Detection.created_at >= from_date)
            .limit(limit)
            .offset(offset)
        )
        results = query.all()
        unlabeled_detections = [Detection(**detection.__dict__) for detection, _ in results]
        urls = [
            s3_service.get_bucket(s3_service.resolve_bucket_name(org_id)).get_public_url(det.bucket_key)
            for det, org_id in results
        ]
    else:
        query = await session.exec(
            select(Detection)  # type: ignore[attr-defined]
            .join(Camera, Detection.camera_id == Camera.id)  # type: ignore[arg-type]
            .where(Detection.is_wildfire.is_(None))  # type: ignore[union-attr]
            .where(Detection.created_at >= from_date)
            .where(Camera.organization_id == token_payload.organization_id)
            .limit(limit)
            .offset(offset)
        )
        results = query.all()
        unlabeled_detections = [Detection(**detection.__dict__) for detection in results]
        bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(token_payload.organization_id))
        urls = [bucket.get_public_url(detection.bucket_key) for detection in unlabeled_detections]

    return [DetectionWithUrl(**detection.model_dump(), url=url) for detection, url in zip(unlabeled_detections, urls)]


@router.patch("/{detection_id}/label", status_code=status.HTTP_200_OK, summary="Label the nature of the detection")
async def label_detection(
    payload: DetectionLabel,
    detection_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    detections: DetectionCRUD = Depends(get_detection_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> Detection:
    telemetry_client.capture(token_payload.sub, event="detections-label", properties={"detection_id": detection_id})
    detection = cast(Detection, await detections.get(detection_id, strict=True))

    if UserRole.ADMIN in token_payload.scopes:
        return await detections.update(detection_id, payload)

    camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return await detections.update(detection_id, payload)


@router.delete("/{detection_id}", status_code=status.HTTP_200_OK, summary="Delete a detection")
async def delete_detection(
    detection_id: int = Path(..., gt=0),
    detections: DetectionCRUD = Depends(get_detection_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN]),
) -> None:
    telemetry_client.capture(token_payload.sub, event="detections-deletion", properties={"detection_id": detection_id})
    detection = cast(Detection, await detections.get(detection_id, strict=True))
    camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
    bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(camera.organization_id))
    bucket.delete_file(detection.bucket_key)
    await detections.delete(detection_id)
