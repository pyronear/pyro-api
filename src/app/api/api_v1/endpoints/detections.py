# Copyright (C) 2024-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from ast import literal_eval
from datetime import datetime, timedelta
from typing import Any, List, cast

import pandas as pd
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Security,
    UploadFile,
    status,
)
from sqlmodel import select

from app.api.dependencies import (
    dispatch_webhook,
    get_alert_crud,
    get_camera_crud,
    get_detection_crud,
    get_jwt,
    get_organization_crud,
    get_pose_crud,
    get_sequence_crud,
    get_webhook_crud,
)
from app.core.config import settings
from app.crud import AlertCRUD, CameraCRUD, DetectionCRUD, OrganizationCRUD, PoseCRUD, SequenceCRUD, WebhookCRUD
from app.models import Alert, AlertSequence, Camera, Detection, Organization, Pose, Role, Sequence, UserRole
from app.schemas.alerts import AlertCreate, AlertUpdate
from app.schemas.detections import (
    BOXES_PATTERN,
    COMPILED_BOXES_PATTERN,
    DetectionCreate,
    DetectionRead,
    DetectionSequence,
    DetectionUrl,
)
from app.schemas.login import TokenPayload
from app.schemas.sequences import SequenceUpdate
from app.services.cones import resolve_cone
from app.services.overlap import compute_overlap
from app.services.slack import slack_client
from app.services.storage import s3_service, upload_file
from app.services.telegram import telegram_client
from app.services.telemetry import telemetry_client

router = APIRouter()


async def _attach_sequence_to_alert(
    sequence_: Sequence,
    camera: Camera,
    cameras: CameraCRUD,
    sequences: SequenceCRUD,
    alerts: AlertCRUD,
) -> None:
    """Assign the given sequence to an alert based on cone/time overlap."""
    org_cameras = await cameras.fetch_all(filters=("organization_id", camera.organization_id))
    camera_by_id = {cam.id: cam for cam in org_cameras}

    if sequence_.camera_id not in camera_by_id:
        camera_by_id[sequence_.camera_id] = camera

    # Fetch recent sequences for the organization based on recency of last_seen_at
    recent_sequences = await sequences.fetch_all(
        in_pair=("camera_id", list(camera_by_id.keys())),
        inequality_pair=(
            "last_seen_at",
            ">",
            datetime.utcnow() - timedelta(seconds=settings.SEQUENCE_RELAXATION_SECONDS),
        ),
    )

    # Ensure the newly created sequence is present
    if all(seq.id != sequence_.id for seq in recent_sequences):
        recent_sequences.append(sequence_)

    # Build DataFrame for overlap computation
    records = []
    for seq in recent_sequences:
        cam = camera_by_id.get(seq.camera_id)
        if cam is None or seq.cone_azimuth is None or seq.cone_angle is None:
            continue
        records.append({
            "id": int(seq.id),
            "lat": float(cam.lat),
            "lon": float(cam.lon),
            "cone_azimuth": float(seq.cone_azimuth),
            "cone_angle": float(seq.cone_angle),
            "is_wildfire": seq.is_wildfire,
            "started_at": seq.started_at,
            "last_seen_at": seq.last_seen_at,
        })

    if not records:
        return

    df = compute_overlap(pd.DataFrame.from_records(records))
    row = df[df["id"] == int(sequence_.id)]
    if row.empty:
        return
    groups = row.iloc[0]["event_groups"]
    locations = row.iloc[0].get("event_smoke_locations", [])
    group_locations = {tuple(g): locations[idx] if idx < len(locations) else None for idx, g in enumerate(groups)}

    seq_by_id = {seq.id: seq for seq in recent_sequences}
    seq_ids = list(seq_by_id.keys())

    # Existing alert links
    session = sequences.session
    mapping: dict[int, set[int]] = {}
    if seq_ids:
        stmt: Any = select(AlertSequence.alert_id, AlertSequence.sequence_id).where(
            AlertSequence.sequence_id.in_(seq_ids)  # type: ignore[attr-defined]
        )
        res = await session.exec(stmt)
        for aid, sid in res:
            mapping.setdefault(int(sid), set()).add(int(aid))

    to_link: List[AlertSequence] = []

    for g in groups:
        g_tuple = tuple(g)
        location = group_locations.get(g_tuple)
        start_at = min(seq_by_id[int(sid)].started_at for sid in g_tuple if int(sid) in seq_by_id)
        last_seen_at = max(seq_by_id[int(sid)].last_seen_at for sid in g_tuple if int(sid) in seq_by_id)
        existing_alert_ids = {aid for sid in g_tuple for aid in mapping.get(int(sid), set())}
        if existing_alert_ids:
            target_alert_id = min(existing_alert_ids)
            # If we now have a location and the alert is missing it (or start_at can be improved), update it
            if isinstance(location, tuple):
                current_alert = cast(Alert, await alerts.get(target_alert_id, strict=True))
                new_start_at = min(start_at, current_alert.started_at) if current_alert.started_at else start_at
                new_last_seen = (
                    max(last_seen_at, current_alert.last_seen_at) if current_alert.last_seen_at else last_seen_at
                )
                if (
                    current_alert.lat is None
                    or current_alert.lon is None
                    or (current_alert.started_at is None or new_start_at < current_alert.started_at)
                    or (current_alert.last_seen_at is None or new_last_seen > current_alert.last_seen_at)
                ):
                    await alerts.update(
                        target_alert_id,
                        AlertUpdate(
                            lat=location[0], lon=location[1], started_at=new_start_at, last_seen_at=new_last_seen
                        ),
                    )
        else:
            alert = await alerts.create(
                AlertCreate(
                    organization_id=camera.organization_id,
                    lat=location[0] if isinstance(location, tuple) else None,
                    lon=location[1] if isinstance(location, tuple) else None,
                    started_at=start_at,
                    last_seen_at=last_seen_at,
                )
            )
            target_alert_id = alert.id
        for sid in g_tuple:
            sid_int = int(sid)
            if target_alert_id in mapping.get(sid_int, set()):
                continue
            mapping.setdefault(sid_int, set()).add(target_alert_id)
            to_link.append(AlertSequence(alert_id=target_alert_id, sequence_id=sid_int))

    if to_link:
        session.add_all(to_link)
        await session.commit()


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
    pose_id: int = Form(..., gt=0, description="pose id of the detection"),
    file: UploadFile = File(..., alias="file"),
    detections: DetectionCRUD = Depends(get_detection_crud),
    webhooks: WebhookCRUD = Depends(get_webhook_crud),
    organizations: OrganizationCRUD = Depends(get_organization_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
    alerts: AlertCRUD = Depends(get_alert_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    poses: PoseCRUD = Depends(get_pose_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[Role.CAMERA]),
) -> Detection:
    telemetry_client.capture(f"camera|{token_payload.sub}", event="detections-create")

    # Throw an error if the format is invalid and can't be captured by the regex
    if not COMPILED_BOXES_PATTERN.fullmatch(bboxes):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid bbox format.")

    try:
        parsed_boxes = literal_eval(bboxes)
    except (ValueError, SyntaxError):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid bbox format.")

    if (
        not isinstance(parsed_boxes, list)
        or len(parsed_boxes) == 0
        or any(not isinstance(box, (list, tuple)) or len(box) != 5 for box in parsed_boxes)
    ):
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid bbox content.")

    bbox_tuples = [tuple(map(float, box)) for box in parsed_boxes]
    if any(xmin >= xmax or ymin >= ymax for xmin, ymin, xmax, ymax, _ in bbox_tuples):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="xmin & ymin are expected to be respectively smaller than xmax & ymax",
        )

    # Upload media
    bucket_key = await upload_file(file, token_payload.organization_id, token_payload.sub)
    pose = cast(Pose, await poses.get(pose_id, strict=True))
    if pose.camera_id != token_payload.sub:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid pose for this camera.")

    # Create one detection per bbox while keeping others_bboxes
    bbox_strs = [f"({','.join(str(v) for v in box)})" for box in bbox_tuples]
    new_detections: List[Detection] = []
    for idx, bbox_str in enumerate(bbox_strs):
        single_bbox_str = f"[{bbox_str}]"
        others = bbox_strs[:idx] + bbox_strs[idx + 1 :]
        others_str = f"[{','.join(others)}]" if others else None
        det = await detections.create(
            DetectionCreate(
                camera_id=token_payload.sub,
                pose_id=pose_id,
                bucket_key=bucket_key,
                bboxes=single_bbox_str,
                others_bboxes=others_str,
            )
        )
        new_detections.append(det)
    det = new_detections[0]
    # Sequence handling
    # Check if there is a sequence that was seen recently
    seq_filters: List[tuple[str, Any]] = [("camera_id", token_payload.sub), ("pose_id", pose_id)]

    sequence = await sequences.fetch_all(
        filters=seq_filters,
        inequality_pair=(
            "last_seen_at",
            ">",
            datetime.utcnow() - timedelta(seconds=settings.SEQUENCE_RELAXATION_SECONDS),
        ),
        order_by="last_seen_at",
        order_desc=True,
        limit=1,
    )

    camera = cast(Camera, await cameras.get(det.camera_id, strict=True))
    # Prepare candidate sequence
    candidate_seq = sequence[0] if sequence else None
    candidate_bbox: tuple[float, float, float, float, float] | None = None
    if candidate_seq:
        last_det_res = await detections.fetch_all(
            filters=[("sequence_id", candidate_seq.id)],
            order_by="created_at",
            order_desc=True,
            limit=1,
        )
        if last_det_res:
            try:
                parsed_last = literal_eval(last_det_res[0].bboxes)
                candidate_bbox = tuple(map(float, parsed_last[0]))  # type: ignore[assignment]
            except (ValueError, SyntaxError):
                candidate_bbox = None

        def parse_bbox(bbox_str: str) -> tuple[float, float, float, float, float]:
            try:
                parsed = literal_eval(bbox_str)
                raw = tuple(map(float, parsed[0][:5]))
                return cast(tuple[float, float, float, float, float], raw)
            except (ValueError, SyntaxError):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Unable to parse detection bounding box."
                )

    def overlaps(b1: tuple[float, float, float, float, float], b2: tuple[float, float, float, float, float]) -> bool:
        xmin1, ymin1, xmax1, ymax1, _ = b1
        xmin2, ymin2, xmax2, ymax2, _ = b2
        return not (xmax1 <= xmin2 or xmax2 <= xmin1 or ymax1 <= ymin2 or ymax2 <= ymin1)

    # Assign detections to sequences based on bbox overlap; create new otherwise
    for det_ in new_detections:
        det_bbox = parse_bbox(det_.bboxes)
        if candidate_seq and candidate_bbox and overlaps(det_bbox, candidate_bbox):
            await sequences.update(candidate_seq.id, SequenceUpdate(last_seen_at=det_.created_at))
            await detections.update(det_.id, DetectionSequence(sequence_id=candidate_seq.id))
            candidate_bbox = det_bbox
        else:
            cone_azimuth, cone_angle = resolve_cone(pose.azimuth, det_.bboxes, camera.angle_of_view)
            sequence_ = await sequences.create(
                Sequence(
                    camera_id=token_payload.sub,
                    pose_id=pose_id,
                    azimuth=pose.azimuth,
                    cone_azimuth=cone_azimuth,
                    cone_angle=cone_angle,
                    started_at=det_.created_at,
                    last_seen_at=det_.created_at,
                )
            )
            await detections.update(det_.id, DetectionSequence(sequence_id=sequence_.id))
            candidate_seq = sequence_
            candidate_bbox = det_bbox

            await _attach_sequence_to_alert(sequence_, camera, cameras, sequences, alerts)

            # Webhooks
            whs = await webhooks.fetch_all()
            if any(whs):
                for webhook in await webhooks.fetch_all():
                    background_tasks.add_task(dispatch_webhook, webhook.url, det_)

            org = None
            # Telegram notifications
            if telegram_client.is_enabled:
                org = cast(Organization, await organizations.get(token_payload.organization_id, strict=True))
                if org.telegram_id:
                    background_tasks.add_task(telegram_client.notify, org.telegram_id, det_.model_dump_json())

            if slack_client.is_enabled:
                if org is None:
                    org = cast(Organization, await organizations.get(token_payload.organization_id, strict=True))
                if org.slack_hook:
                    bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(token_payload.organization_id))
                    url = bucket.get_public_url(det_.bucket_key)

                    background_tasks.add_task(
                        slack_client.notify, org.slack_hook, det_.model_dump_json(), url, camera.name
                    )

    det = cast(Detection, await detections.get(det.id, strict=True))
    return DetectionRead(**det.model_dump())


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
    return DetectionRead(**detection.model_dump())


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
) -> List[DetectionRead]:
    telemetry_client.capture(token_payload.sub, event="detections-fetch")
    if UserRole.ADMIN in token_payload.scopes:
        return [DetectionRead(**elt.model_dump()) for elt in await detections.fetch_all()]

    cameras_list = await cameras.fetch_all(filters=("organization_id", token_payload.organization_id))
    camera_ids = [camera.id for camera in cameras_list]

    return [
        DetectionRead(**elt.model_dump())
        for elt in await detections.fetch_all(in_pair=("camera_id", camera_ids), order_by="id")
    ]


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
