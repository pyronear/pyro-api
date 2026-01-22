# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


import json
import re
from ast import literal_eval
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, cast

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
from fastapi.encoders import jsonable_encoder
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

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
    BOX_PATTERN,
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


def _extract_bbox_strings(bboxes: str) -> List[str]:
    return [match.group(0) for match in re.finditer(BOX_PATTERN, bboxes)]


def _bbox_list_to_str(bboxes: List[str]) -> str:
    return f"[{','.join(bboxes)}]"


def _parse_bbox(bbox_str: str) -> Tuple[float, float, float, float, float]:
    try:
        bbox = literal_eval(bbox_str)
    except (SyntaxError, ValueError) as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid bbox format.") from exc
    if not isinstance(bbox, tuple) or len(bbox) != 5:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid bbox format.")
    return cast(Tuple[float, float, float, float, float], bbox)


def _bboxes_overlap(
    left: Tuple[float, float, float, float, float],
    right: Tuple[float, float, float, float, float],
) -> bool:
    lx_min, ly_min, lx_max, ly_max, _ = left
    rx_min, ry_min, rx_max, ry_max, _ = right
    inter_w = min(lx_max, rx_max) - max(lx_min, rx_min)
    inter_h = min(ly_max, ry_max) - max(ly_min, ry_min)
    return inter_w > 0 and inter_h > 0


async def _get_last_bbox_for_sequence(
    detections: DetectionCRUD,
    sequence_id: int,
) -> Optional[Tuple[float, float, float, float, float]]:
    dets = await detections.fetch_all(
        filters=("sequence_id", sequence_id),
        order_by="created_at",
        order_desc=True,
        limit=1,
    )
    if not dets:
        return None
    bbox_strs = _extract_bbox_strings(dets[0].bbox)
    if not bbox_strs:
        return None
    return _parse_bbox(bbox_strs[0])


async def _get_camera_by_id(
    camera: Camera,
    cameras: CameraCRUD,
    sequence_camera_id: int,
) -> Dict[int, Camera]:
    org_cameras = await cameras.fetch_all(filters=("organization_id", camera.organization_id))
    camera_by_id = {cam.id: cam for cam in org_cameras}
    if sequence_camera_id not in camera_by_id:
        camera_by_id[sequence_camera_id] = camera
    return camera_by_id


async def _get_recent_sequences(
    sequences: SequenceCRUD,
    camera_ids: List[int],
    sequence_: Sequence,
) -> List[Sequence]:
    recent_sequences = await sequences.fetch_all(
        in_pair=("camera_id", camera_ids),
        inequality_pair=(
            "last_seen_at",
            ">",
            datetime.utcnow() - timedelta(seconds=settings.SEQUENCE_RELAXATION_SECONDS),
        ),
    )
    if all(seq.id != sequence_.id for seq in recent_sequences):
        recent_sequences.append(sequence_)
    return recent_sequences


def _build_overlap_records(
    recent_sequences: List[Sequence],
    camera_by_id: Dict[int, Camera],
) -> List[Dict[str, Any]]:
    records: List[Dict[str, Any]] = []
    for seq in recent_sequences:
        cam = camera_by_id.get(seq.camera_id)
        if cam is None or seq.sequence_azimuth is None or seq.cone_angle is None:
            continue
        records.append({
            "id": int(seq.id),
            "lat": float(cam.lat),
            "lon": float(cam.lon),
            "sequence_azimuth": float(seq.sequence_azimuth),
            "cone_angle": float(seq.cone_angle),
            "is_wildfire": seq.is_wildfire,
            "started_at": seq.started_at,
            "last_seen_at": seq.last_seen_at,
        })
    return records


def _resolve_groups_and_locations(
    records: List[Dict[str, Any]],
    sequence_id: int,
) -> Optional[Tuple[List[Tuple[int, ...]], Dict[Tuple[int, ...], Optional[Tuple[float, float]]]]]:
    if not records:
        return None
    df = compute_overlap(pd.DataFrame.from_records(records))
    row = df[df["id"] == int(sequence_id)]
    if row.empty:
        return None
    groups = [tuple(g) for g in row.iloc[0]["event_groups"]]
    locations = row.iloc[0].get("event_smoke_locations", [])
    group_locations: Dict[Tuple[int, ...], Optional[Tuple[float, float]]] = {}
    for idx, group in enumerate(groups):
        group_locations[group] = locations[idx] if idx < len(locations) else None
    return groups, group_locations


async def _fetch_alert_mapping(session: AsyncSession, seq_ids: List[int]) -> Dict[int, Set[int]]:
    mapping: Dict[int, Set[int]] = {}
    if not seq_ids:
        return mapping
    stmt: Any = select(AlertSequence.alert_id, AlertSequence.sequence_id).where(
        AlertSequence.sequence_id.in_(seq_ids)  # type: ignore[attr-defined]
    )
    res = await session.exec(stmt)
    for aid, sid in res:
        mapping.setdefault(int(sid), set()).add(int(aid))
    return mapping


def _group_time_bounds(
    group: Tuple[int, ...],
    seq_by_id: Dict[int, Sequence],
) -> Tuple[datetime, datetime]:
    start_at = min(seq_by_id[int(sid)].started_at for sid in group if int(sid) in seq_by_id)
    last_seen_at = max(seq_by_id[int(sid)].last_seen_at for sid in group if int(sid) in seq_by_id)
    return start_at, last_seen_at


def _collect_existing_alert_ids(group: Tuple[int, ...], mapping: Dict[int, Set[int]]) -> Set[int]:
    return {aid for sid in group for aid in mapping.get(int(sid), set())}


async def _maybe_update_alert(
    alerts: AlertCRUD,
    target_alert_id: int,
    location: Tuple[float, float],
    start_at: datetime,
    last_seen_at: datetime,
) -> None:
    current_alert = cast(Alert, await alerts.get(target_alert_id, strict=True))
    new_start_at = min(start_at, current_alert.started_at) if current_alert.started_at else start_at
    new_last_seen = max(last_seen_at, current_alert.last_seen_at) if current_alert.last_seen_at else last_seen_at
    if (
        current_alert.lat is None
        or current_alert.lon is None
        or (current_alert.started_at is None or new_start_at < current_alert.started_at)
        or (current_alert.last_seen_at is None or new_last_seen > current_alert.last_seen_at)
    ):
        await alerts.update(
            target_alert_id,
            AlertUpdate(lat=location[0], lon=location[1], started_at=new_start_at, last_seen_at=new_last_seen),
        )


async def _get_or_create_alert_id(
    existing_alert_ids: Set[int],
    location: Optional[Tuple[float, float]],
    organization_id: int,
    start_at: datetime,
    last_seen_at: datetime,
    alerts: AlertCRUD,
) -> int:
    if existing_alert_ids:
        target_alert_id = min(existing_alert_ids)
        if isinstance(location, tuple):
            await _maybe_update_alert(alerts, target_alert_id, location, start_at, last_seen_at)
        return target_alert_id
    alert = await alerts.create(
        AlertCreate(
            organization_id=organization_id,
            lat=location[0] if isinstance(location, tuple) else None,
            lon=location[1] if isinstance(location, tuple) else None,
            started_at=start_at,
            last_seen_at=last_seen_at,
        )
    )
    return alert.id


def _build_links_for_group(
    group: Tuple[int, ...],
    target_alert_id: int,
    mapping: Dict[int, Set[int]],
) -> List[AlertSequence]:
    links: List[AlertSequence] = []
    for sid in group:
        sid_int = int(sid)
        if target_alert_id in mapping.get(sid_int, set()):
            continue
        mapping.setdefault(sid_int, set()).add(target_alert_id)
        links.append(AlertSequence(alert_id=target_alert_id, sequence_id=sid_int))
    return links


async def _attach_sequence_to_alert(
    sequence_: Sequence,
    camera: Camera,
    cameras: CameraCRUD,
    sequences: SequenceCRUD,
    alerts: AlertCRUD,
) -> None:
    """Assign the given sequence to an alert based on cone/time overlap."""
    camera_by_id = await _get_camera_by_id(camera, cameras, sequence_.camera_id)

    # Fetch recent sequences for the organization based on recency of last_seen_at
    recent_sequences = await _get_recent_sequences(sequences, list(camera_by_id.keys()), sequence_)

    # Build DataFrame for overlap computation
    records = _build_overlap_records(recent_sequences, camera_by_id)
    resolved = _resolve_groups_and_locations(records, int(sequence_.id))
    if resolved is None:
        return
    groups, group_locations = resolved

    seq_by_id = {seq.id: seq for seq in recent_sequences}
    seq_ids = list(seq_by_id.keys())

    # Existing alert links
    session = sequences.session
    mapping = await _fetch_alert_mapping(session, seq_ids)

    to_link: List[AlertSequence] = []

    for g in groups:
        location = group_locations.get(g)
        start_at, last_seen_at = _group_time_bounds(g, seq_by_id)
        existing_alert_ids = _collect_existing_alert_ids(g, mapping)
        target_alert_id = await _get_or_create_alert_id(
            existing_alert_ids,
            location,
            camera.organization_id,
            start_at,
            last_seen_at,
            alerts,
        )
        to_link.extend(_build_links_for_group(g, target_alert_id, mapping))

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
    if any(box[0] >= box[2] or box[1] >= box[3] for box in COMPILED_BOXES_PATTERN.findall(bboxes)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="xmin & ymin are expected to be respectively smaller than xmax & ymax",
        )

    # Upload media
    bucket_key = await upload_file(file, token_payload.organization_id, token_payload.sub)
    pose = cast(Pose, await poses.get(pose_id, strict=True))
    if pose.camera_id != token_payload.sub:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")

    bbox_strings = _extract_bbox_strings(bboxes)
    if not bbox_strings:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid bbox format.")

    created: List[Detection] = []
    camera = cast(Camera, await cameras.get(token_payload.sub, strict=True))

    for idx, bbox_str in enumerate(bbox_strings):
        single_bboxes = _bbox_list_to_str([bbox_str])
        other_bbox_strings = bbox_strings[:idx] + bbox_strings[idx + 1 :]
        others_bboxes = _bbox_list_to_str(other_bbox_strings) if other_bbox_strings else None
        det = await detections.create(
            DetectionCreate(
                camera_id=token_payload.sub,
                pose_id=pose_id,
                bucket_key=bucket_key,
                bbox=single_bboxes,
                others_bboxes=others_bboxes,
            )
        )

        det_bbox = _parse_bbox(bbox_str)
        # Sequence handling
        # Check if there is a sequence that was seen recently
        candidate_sequences = await sequences.fetch_all(
            filters=[("camera_id", token_payload.sub), ("pose_id", pose_id)],
            inequality_pair=(
                "last_seen_at",
                ">",
                datetime.utcnow() - timedelta(seconds=settings.SEQUENCE_RELAXATION_SECONDS),
            ),
            order_by="last_seen_at",
            order_desc=True,
        )
        matched_sequence: Optional[Sequence] = None
        for seq in candidate_sequences:
            if seq.id is None:
                continue
            last_bbox = await _get_last_bbox_for_sequence(detections, seq.id)
            if last_bbox is not None and _bboxes_overlap(last_bbox, det_bbox):
                matched_sequence = seq
                break

        if matched_sequence is not None:
            await sequences.update(matched_sequence.id, SequenceUpdate(last_seen_at=det.created_at))
            det = await detections.update(det.id, DetectionSequence(sequence_id=matched_sequence.id))
        else:
            det_filters: List[tuple[str, Any]] = [
                ("camera_id", token_payload.sub),
                ("pose_id", pose_id),
                ("sequence_id", None),
            ]
            dets_ = await detections.fetch_all(
                filters=det_filters,
                inequality_pair=(
                    "created_at",
                    ">",
                    datetime.utcnow() - timedelta(seconds=settings.SEQUENCE_MIN_INTERVAL_SECONDS),
                ),
                order_by="created_at",
                order_desc=False,
            )
            overlapping_dets: List[Detection] = []
            for cand in dets_:
                cand_bbox_strs = _extract_bbox_strings(cand.bbox)
                if not cand_bbox_strs:
                    continue
                cand_bbox = _parse_bbox(cand_bbox_strs[0])
                if _bboxes_overlap(cand_bbox, det_bbox):
                    overlapping_dets.append(cand)

            if len(overlapping_dets) >= settings.SEQUENCE_MIN_INTERVAL_DETS:
                first_det = min(overlapping_dets, key=lambda item: item.created_at)
                cone_azimuth, cone_angle = resolve_cone(pose.azimuth, first_det.bbox, camera.angle_of_view)
                sequence_ = await sequences.create(
                    Sequence(
                        camera_id=token_payload.sub,
                        pose_id=pose_id,
                        camera_azimuth=pose.azimuth,
                        sequence_azimuth=cone_azimuth,
                        cone_angle=cone_angle,
                        started_at=first_det.created_at,
                        last_seen_at=det.created_at,
                    )
                )
                for det_ in overlapping_dets:
                    updated = await detections.update(det_.id, DetectionSequence(sequence_id=sequence_.id))
                    if det_.id == det.id:
                        det = updated

                await _attach_sequence_to_alert(sequence_, camera, cameras, sequences, alerts)

                # Webhooks
                whs = await webhooks.fetch_all()
                if any(whs):
                    for webhook in await webhooks.fetch_all():
                        background_tasks.add_task(dispatch_webhook, webhook.url, det)

                org = None
                # Telegram notifications
                if telegram_client.is_enabled:
                    org = cast(Organization, await organizations.get(token_payload.organization_id, strict=True))
                    if org.telegram_id:
                        background_tasks.add_task(telegram_client.notify, org.telegram_id, det.model_dump_json())

                if slack_client.is_enabled:
                    if org is None:
                        org = cast(Organization, await organizations.get(token_payload.organization_id, strict=True))
                    if org.slack_hook:
                        bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(token_payload.organization_id))
                        url = bucket.get_public_url(det.bucket_key)

                        slack_payload = jsonable_encoder(det)
                        slack_payload["pose_azimuth"] = pose.azimuth
                        slack_payload["sequence_azimuth"] = sequence_.sequence_azimuth
                        background_tasks.add_task(
                            slack_client.notify, org.slack_hook, json.dumps(slack_payload), url, camera.name
                        )

        created.append(det)

    first_det = cast(Detection, await detections.get(created[0].id, strict=True))
    return DetectionRead(**first_det.model_dump())


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
