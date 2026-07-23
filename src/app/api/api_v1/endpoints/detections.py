# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


import itertools
import logging
import re
from ast import literal_eval
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set, Tuple, cast

import pandas as pd
from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Path,
    Security,
    UploadFile,
    status,
)
from sqlmodel import delete, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import (
    get_camera_crud,
    get_detection_crud,
    get_jwt,
    get_pose_crud,
    get_sequence_crud,
)
from app.core.config import settings
from app.core.time import utcnow
from app.crud import AlertCRUD, CameraCRUD, DetectionCRUD, PoseCRUD, SequenceCRUD
from app.models import Alert, AlertSequence, Camera, Detection, Pose, Role, Sequence, UserRole
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
from app.services.overlap import compute_overlap, haversine_km
from app.services.sequence_confidence import max_conf_from_bboxes
from app.services.storage import s3_service, upload_file
from app.services.telemetry import telemetry_client

logger = logging.getLogger("uvicorn.error")

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
    tolerance: float = 0.0,
) -> bool:
    # A negative intersection is a gap: allow up to `tolerance` (relative coords) per axis
    # so a plume whose bbox drifts between frames still matches its sequence.
    lx_min, ly_min, lx_max, ly_max, _ = left
    rx_min, ry_min, rx_max, ry_max, _ = right
    inter_w = min(lx_max, rx_max) - max(lx_min, rx_min)
    inter_h = min(ly_max, ry_max) - max(ly_min, ry_min)
    return inter_w > -tolerance and inter_h > -tolerance


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
            utcnow() - timedelta(seconds=settings.SEQUENCE_RELAXATION_SECONDS),
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
        # Only validated sequences are eligible for triangulation (as target or partner).
        if not seq.is_validated:
            continue
        records.append({
            "id": int(seq.id),
            "pose_id": seq.pose_id,
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
    location: Optional[Tuple[float, float]],
    start_at: datetime,
    last_seen_at: datetime,
) -> None:
    current_alert = cast(Alert, await alerts.get(target_alert_id, strict=True))
    new_start_at = min(start_at, current_alert.started_at) if current_alert.started_at else start_at
    new_last_seen = max(last_seen_at, current_alert.last_seen_at) if current_alert.last_seen_at else last_seen_at
    # A location-less group (e.g. same-mast only) still widens the time bounds but must
    # not erase a location the alert already has.
    lat, lon = location if location is not None else (current_alert.lat, current_alert.lon)
    if (
        (location is not None and (current_alert.lat is None or current_alert.lon is None))
        or (current_alert.started_at is None or new_start_at < current_alert.started_at)
        or (current_alert.last_seen_at is None or new_last_seen > current_alert.last_seen_at)
    ):
        await alerts.update(
            target_alert_id,
            AlertUpdate(lat=lat, lon=lon, started_at=new_start_at, last_seen_at=new_last_seen),
        )


async def _filter_candidate_alert_ids(
    existing_alert_ids: Set[int],
    location: Optional[Tuple[float, float]],
    alerts: AlertCRUD,
) -> Set[int]:
    if location is None or not existing_alert_ids:
        return existing_alert_ids
    kept: Set[int] = set()
    for aid in existing_alert_ids:
        alert = cast(Alert, await alerts.get(aid, strict=True))
        if alert.lat is None or alert.lon is None:
            kept.add(aid)
            continue
        if haversine_km(location[0], location[1], alert.lat, alert.lon) <= settings.ALERT_MERGE_MAX_DISTANCE_KM:
            kept.add(aid)
    return kept


async def _merge_alerts(
    target_alert_id: int,
    absorbed_ids: Set[int],
    alerts: AlertCRUD,
    queued_links: Optional[List[AlertSequence]] = None,
) -> None:
    """Absorb duplicate alerts into the target: relink their sequences, widen the target's
    time bounds, inherit a location if the target has none, then delete the absorbed rows."""
    session = alerts.session
    target = cast(Alert, await alerts.get(target_alert_id, strict=True))
    absorbed = sorted(await alerts.get_in(list(absorbed_ids), "id"), key=lambda a: a.id)

    links_stmt: Any = select(AlertSequence).where(
        AlertSequence.alert_id.in_([target_alert_id, *absorbed_ids])  # type: ignore[attr-defined]
    )
    links = (await session.exec(links_stmt)).all()
    target_seq_ids = {link.sequence_id for link in links if link.alert_id == target_alert_id}
    # Links to the target queued by the caller but not committed yet count as existing,
    # otherwise relinking would insert the same composite key twice.
    target_seq_ids |= {link.sequence_id for link in queued_links or [] if link.alert_id == target_alert_id}
    for link in links:
        if link.alert_id == target_alert_id or link.sequence_id in target_seq_ids:
            continue
        target_seq_ids.add(link.sequence_id)
        session.add(AlertSequence(alert_id=target_alert_id, sequence_id=link.sequence_id))

    target.started_at = min([target.started_at, *[a.started_at for a in absorbed]])
    target.last_seen_at = max([target.last_seen_at, *[a.last_seen_at for a in absorbed]])
    if target.lat is None or target.lon is None:
        located = next((a for a in absorbed if a.lat is not None and a.lon is not None), None)
        if located is not None:
            target.lat = located.lat
            target.lon = located.lon
    session.add(target)

    delete_links_stmt: Any = delete(AlertSequence).where(cast(Any, AlertSequence.alert_id).in_(list(absorbed_ids)))
    await session.exec(delete_links_stmt)
    delete_alerts_stmt: Any = delete(Alert).where(cast(Any, Alert.id).in_(list(absorbed_ids)))
    await session.exec(delete_alerts_stmt)
    await session.commit()


def _rewrite_after_merge(
    mapping: Dict[int, Set[int]],
    to_link: List[AlertSequence],
    absorbed_ids: Set[int],
    target_alert_id: int,
) -> None:
    """Point in-memory attach state at the merge survivor so later groups neither reference
    deleted alerts nor duplicate links the merge already created."""
    kept: List[AlertSequence] = []
    seen: Set[Tuple[int, int]] = set()
    for link in to_link:
        if link.alert_id in absorbed_ids:
            if target_alert_id in mapping.get(link.sequence_id, set()):
                # The merge relinked this sequence (or a link is already queued): drop it.
                continue
            link.alert_id = target_alert_id
        pair = (link.alert_id, link.sequence_id)
        if pair in seen:
            continue
        seen.add(pair)
        kept.append(link)
    to_link[:] = kept
    for alert_ids in mapping.values():
        if alert_ids & absorbed_ids:
            alert_ids -= absorbed_ids
            alert_ids.add(target_alert_id)


async def _candidates_are_one_event(candidates: Set[int], alerts: AlertCRUD) -> bool:
    """Whether every located candidate sits within the merge radius of the others.

    A location-less group passes the distance filter against every candidate, so on its
    own it says nothing about which distant alerts are the same event — e.g. two cameras
    on one mast can each watch a different fire along the same bearing."""
    located = []
    for aid in candidates:
        alert = cast(Alert, await alerts.get(aid, strict=True))
        if alert.lat is not None and alert.lon is not None:
            located.append((alert.lat, alert.lon))
    return all(
        haversine_km(lat1, lon1, lat2, lon2) <= settings.ALERT_MERGE_MAX_DISTANCE_KM
        for (lat1, lon1), (lat2, lon2) in itertools.combinations(located, 2)
    )


async def _get_or_create_alert_id(
    existing_alert_ids: Set[int],
    location: Optional[Tuple[float, float]],
    organization_id: int,
    start_at: datetime,
    last_seen_at: datetime,
    alerts: AlertCRUD,
    queued_links: Optional[List[AlertSequence]] = None,
) -> Tuple[int, Set[int]]:
    """Pick the alert a group belongs to, merging duplicates when the group's sequences
    span several compatible alerts. Returns the target alert id and the absorbed ids."""
    candidates = await _filter_candidate_alert_ids(existing_alert_ids, location, alerts)
    if candidates:
        target_alert_id = min(candidates)
        absorbed_ids = set(candidates) - {target_alert_id}
        if absorbed_ids and location is None and not await _candidates_are_one_event(candidates, alerts):
            # Without a triangulated location, a group bridging distant alerts is not
            # merge evidence: link to the oldest one and leave the others alive.
            absorbed_ids = set()
        if absorbed_ids:
            await _merge_alerts(target_alert_id, absorbed_ids, alerts, queued_links)
        await _maybe_update_alert(alerts, target_alert_id, location, start_at, last_seen_at)
        return target_alert_id, absorbed_ids
    alert = await alerts.create(
        AlertCreate(
            organization_id=organization_id,
            lat=location[0] if isinstance(location, tuple) else None,
            lon=location[1] if isinstance(location, tuple) else None,
            started_at=start_at,
            last_seen_at=last_seen_at,
        )
    )
    return alert.id, set()


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
) -> Optional[int]:
    """Assign the given sequence to an alert based on cone/time overlap."""
    camera_by_id = await _get_camera_by_id(camera, cameras, sequence_.camera_id)

    # Fetch recent sequences for the organization based on recency of last_seen_at
    recent_sequences = await _get_recent_sequences(sequences, list(camera_by_id.keys()), sequence_)

    # Build DataFrame for overlap computation
    records = _build_overlap_records(recent_sequences, camera_by_id)
    resolved = _resolve_groups_and_locations(records, int(sequence_.id))
    if resolved is None:
        return None
    groups, group_locations = resolved

    seq_by_id = {seq.id: seq for seq in recent_sequences}
    seq_ids = list(seq_by_id.keys())

    # Existing alert links
    session = sequences.session
    mapping = await _fetch_alert_mapping(session, seq_ids)

    to_link: List[AlertSequence] = []
    alert_id: Optional[int] = None

    for g in groups:
        location = group_locations.get(g)
        start_at, last_seen_at = _group_time_bounds(g, seq_by_id)
        existing_alert_ids = _collect_existing_alert_ids(g, mapping)
        target_alert_id, absorbed_ids = await _get_or_create_alert_id(
            existing_alert_ids,
            location,
            camera.organization_id,
            start_at,
            last_seen_at,
            alerts,
            queued_links=to_link,
        )
        if absorbed_ids:
            _rewrite_after_merge(mapping, to_link, absorbed_ids, target_alert_id)
        if int(sequence_.id) in g:
            alert_id = target_alert_id
        to_link.extend(_build_links_for_group(g, target_alert_id, mapping))

    if to_link:
        session.add_all(to_link)
        await session.commit()

    return alert_id


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new wildfire detection")
async def create_detection(
    bboxes: str = Form(
        ...,
        description="string representation of list of detection localizations, each represented as a tuple of relative coords (max 3 decimals) in order: xmin, ymin, xmax, ymax, conf",
        pattern=BOXES_PATTERN,
        min_length=2,
        max_length=settings.MAX_BBOX_STR_LENGTH,
    ),
    pose_id: int = Form(..., gt=0, description="pose id of the detection"),
    file: UploadFile = File(..., alias="file"),
    crop_files: Optional[List[UploadFile]] = File(None, alias="crop"),
    detections: DetectionCRUD = Depends(get_detection_crud),
    sequences: SequenceCRUD = Depends(get_sequence_crud),
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

    # Authorize before any S3 upload to avoid orphan objects on 403
    pose = cast(Pose, await poses.get(pose_id, strict=True))
    if pose.camera_id != token_payload.sub:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    if not pose.active:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Pose is not active.")

    bbox_strings = _extract_bbox_strings(bboxes)
    if not bbox_strings:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid bbox format.")

    # Validate crop/bbox alignment before any S3 upload to avoid orphan objects.
    # Each crop frames a single object, so there must be exactly one crop per bbox (or none at all).
    crops = crop_files or []
    if crops and len(crops) != len(bbox_strings):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Number of crops must match the number of bboxes.",
        )

    # Upload media
    bucket_key = await upload_file(file, token_payload.organization_id, token_payload.sub)
    crop_bucket_keys: List[Optional[str]] = [None] * len(bbox_strings)
    for idx, crop in enumerate(crops):
        # Prefix with the bbox index so byte-identical crops in the same request still get
        # distinct keys; each detection then owns its crop object (safe to delete independently).
        crop_bucket_keys[idx] = await upload_file(
            crop, token_payload.organization_id, token_payload.sub, key_prefix=f"crop_{idx}_"
        )

    created: List[Detection] = []
    camera = cast(Camera, await cameras.get(token_payload.sub, strict=True))
    # sequences touched by this request, to mark due for validation (DB-backed queue).
    affected_sequences: Set[int] = set()

    for idx, bbox_str in enumerate(bbox_strings):
        single_bboxes = _bbox_list_to_str([bbox_str])
        other_bbox_strings = bbox_strings[:idx] + bbox_strings[idx + 1 :]
        others_bboxes = _bbox_list_to_str(other_bbox_strings) if other_bbox_strings else None
        det = await detections.create(
            DetectionCreate(
                camera_id=token_payload.sub,
                pose_id=pose_id,
                bucket_key=bucket_key,
                crop_bucket_key=crop_bucket_keys[idx],
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
                utcnow() - timedelta(seconds=settings.SEQUENCE_RELAXATION_SECONDS),
            ),
            order_by="last_seen_at",
            order_desc=True,
        )
        matched_sequence: Optional[Sequence] = None
        for seq in candidate_sequences:
            if seq.id is None:
                continue
            last_bbox = await _get_last_bbox_for_sequence(detections, seq.id)
            if last_bbox is not None and _bboxes_overlap(last_bbox, det_bbox, settings.SEQUENCE_BBOX_TOLERANCE):
                matched_sequence = seq
                break

        if matched_sequence is not None:
            await sequences.update(matched_sequence.id, SequenceUpdate(last_seen_at=det.created_at))
            det = await detections.update(det.id, DetectionSequence(sequence_id=matched_sequence.id))
            # Only the primary bbox tracks the sequence; siblings in others_bboxes are unrelated detections.
            det_max_conf = max_conf_from_bboxes(det.bbox)
            if det_max_conf is not None:
                await sequences.bump_max_conf(matched_sequence.id, det_max_conf)
            affected_sequences.add(matched_sequence.id)
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
                    utcnow() - timedelta(seconds=settings.SEQUENCE_MIN_INTERVAL_SECONDS),
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
                if _bboxes_overlap(cand_bbox, det_bbox, settings.SEQUENCE_BBOX_TOLERANCE):
                    overlapping_dets.append(cand)

            if len(overlapping_dets) >= settings.SEQUENCE_MIN_INTERVAL_DETS:
                first_det = min(overlapping_dets, key=lambda item: item.created_at)
                cone_azimuth, cone_angle = resolve_cone(pose.azimuth, first_det.bbox, camera.angle_of_view)
                seq_max_conf = max_conf_from_bboxes(*[d.bbox for d in overlapping_dets])
                sequence_ = await sequences.create(
                    Sequence(
                        camera_id=token_payload.sub,
                        pose_id=pose_id,
                        camera_azimuth=pose.azimuth,
                        sequence_azimuth=cone_azimuth,
                        cone_angle=cone_angle,
                        started_at=first_det.created_at,
                        last_seen_at=det.created_at,
                        max_conf=seq_max_conf,
                    )
                )
                for det_ in overlapping_dets:
                    updated = await detections.update(det_.id, DetectionSequence(sequence_id=sequence_.id))
                    if det_.id == det.id:
                        det = updated
                affected_sequences.add(sequence_.id)

        created.append(det)

    # Mark touched sequences due for validation (idempotent: one queue entry per sequence,
    # whichever uvicorn worker received the detection). The per-process validation worker
    # claims due sequences from the DB and runs the gated pipeline: triangulation and ALL
    # notification channels (webhooks, Telegram, Slack) fire only once validated.
    for seq_id in affected_sequences:
        await sequences.enqueue_validation(seq_id)

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

    if token_payload.is_admin:
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

    camera = cast(Camera, await cameras.get(detection.camera_id, strict=True))
    if not token_payload.is_admin and token_payload.organization_id != camera.organization_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(camera.organization_id))
    crop_url = (
        bucket.get_public_url(detection.crop_bucket_key, verify_exists=False) if detection.crop_bucket_key else None
    )
    return DetectionUrl(url=bucket.get_public_url(detection.bucket_key, verify_exists=False), crop_url=crop_url)


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the detections")
async def fetch_detections(
    detections: DetectionCRUD = Depends(get_detection_crud),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[DetectionRead]:
    telemetry_client.capture(token_payload.sub, event="detections-fetch")
    if token_payload.is_admin:
        return [DetectionRead(**elt.model_dump()) for elt in await detections.fetch_all(order_by="id")]

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
    if detection.crop_bucket_key:
        bucket.delete_file(detection.crop_bucket_key)
    await detections.delete(detection_id)
