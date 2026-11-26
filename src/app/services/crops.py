# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

"""Crops of the detections of a validated sequence, cut by the API from the engine's native crops.

All the crops of a sequence are cut from the same region of the frame (``sequences.crop_box``),
so that played one after the other they show a still picture centered on the object. The region
covers the bboxes of the whole sequence: when a new bbox leaves it, it grows and every crop of the
sequence is cut again.

Sequences to refresh are queued in the DB (``sequences.crops_due_at``) and claimed by one worker
loop per uvicorn process, like the validation jobs: nothing is lost on a restart.
"""

import asyncio
import io
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from anyio import to_thread
from botocore.exceptions import ClientError
from fastapi import UploadFile
from PIL import Image

from app.crud import CameraCRUD, DetectionCRUD, SequenceCRUD
from app.db import session_factory
from app.models import Detection
from app.schemas.detections import EMPTY_BBOXES
from app.services.images import delete_objects
from app.services.storage import S3Bucket, s3_service, upload_file

logger = logging.getLogger("uvicorn.error")

__all__ = ["crop_worker_loop", "process_next_due_crops", "refresh_sequence_crops", "square_box"]

Box = Tuple[float, float, float, float]

# Same crop as the one the engine used to send: a square around the bboxes, resized to 224x224
CROP_SIZE = 224
# Margin around the bboxes, as a fraction of their longest side. It is also the room the object has
# to grow before every crop of the sequence is cut again: raise it for fewer, wider crops.
CROP_PADDING = 0.2
CROP_JPEG_QUALITY = 90

POLL_SECONDS = 2.0
# ponytail: a refresh longer than the lease is taken over by a second worker and its work is thrown
# away. Refresh in batches if sequences get long enough for that.
LEASE_SECONDS = 600.0
# ponytail: no cap on attempts, a job that always fails is retried at this pace until it is fixed
RETRY_DELAY_SECONDS = 30.0


def _parse_box(box: str) -> Box:
    xmin, ymin, xmax, ymax = (float(value) for value in box.strip("()").split(","))
    return xmin, ymin, xmax, ymax


def _contains(outer: Box, inner: Box) -> bool:
    return outer[0] <= inner[0] and outer[1] <= inner[1] and inner[2] <= outer[2] and inner[3] <= outer[3]


def square_box(bboxes: Box, frame_width: float, frame_height: float) -> Box:
    """Region of the frame to crop around `bboxes` (the region covering every bbox), as relative coordinates.

    A square in pixels, with CROP_PADDING around the longest side of `bboxes`. It is centered on
    them, shifted back inside the frame near an edge, and no larger than the frame.
    """
    xmin, ymin, xmax, ymax = (
        bboxes[0] * frame_width,
        bboxes[1] * frame_height,
        bboxes[2] * frame_width,
        bboxes[3] * frame_height,
    )
    side = min(max(xmax - xmin, ymax - ymin) * (1 + CROP_PADDING), frame_width, frame_height)
    left = min(max((xmin + xmax - side) / 2, 0), frame_width - side)
    top = min(max((ymin + ymax - side) / 2, 0), frame_height - side)
    return (
        round(left / frame_width, 6),
        round(top / frame_height, 6),
        round((left + side) / frame_width, 6),
        round((top + side) / frame_height, 6),
    )


def _cut(image: bytes, region: Box) -> bytes:
    """CROP_SIZE x CROP_SIZE JPEG of a region of an image, given as relative coordinates"""
    picture = Image.open(io.BytesIO(image)).convert("RGB")
    width, height = picture.size
    crop = picture.crop((
        round(region[0] * width),
        round(region[1] * height),
        round(region[2] * width),
        round(region[3] * height),
    ))
    buffer = io.BytesIO()
    crop.resize((CROP_SIZE, CROP_SIZE), Image.Resampling.LANCZOS).save(buffer, format="JPEG", quality=CROP_JPEG_QUALITY)
    return buffer.getvalue()


def _download(bucket: S3Bucket, bucket_key: str) -> Optional[bytes]:
    try:
        return bucket.download_file(bucket_key)
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") != "NoSuchKey":
            raise
        return None


def _frame_size(bucket: S3Bucket, detections: List[Detection]) -> Optional[Tuple[float, float]]:
    """Size in pixels of the frame the native crops come from, read from the first usable one"""
    for detection in detections:
        native_crop = _download(bucket, detection.native_crop_bucket_key or "")
        if native_crop is None:
            continue
        try:
            width, height = Image.open(io.BytesIO(native_crop)).size
        except OSError:
            continue
        window = _parse_box(detection.native_crop_window or "")
        return width / (window[2] - window[0]), height / (window[3] - window[1])
    return None


def _detection_crop(bucket: S3Bucket, detection: Detection, box: Box) -> Optional[bytes]:
    """Crop of a detection for the region `box` of its frame, None if its image can't be used"""
    window = _parse_box(detection.native_crop_window or "")
    if _contains(window, box):
        key = detection.native_crop_bucket_key or ""
        width, height = window[2] - window[0], window[3] - window[1]
        region = (
            (box[0] - window[0]) / width,
            (box[1] - window[1]) / height,
            (box[2] - window[0]) / width,
            (box[3] - window[1]) / height,
        )
    else:
        # The region is larger than the native crop: at that size the downscaled frame has enough pixels
        key, region = detection.bucket_key, box
    image = _download(bucket, key)
    if image is not None:
        try:
            return _cut(image, region)
        except (OSError, ValueError) as e:
            logger.warning(f"Could not crop detection {detection.id} from {key}: {e}")
            return None
    logger.warning(f"Could not crop detection {detection.id}: {key} is missing")
    return None


async def refresh_sequence_crops(sequence_id: int, lease_until: Optional[datetime] = None) -> None:
    """Cut the missing crops of a validated sequence, or all of them when its crop box has to grow.

    Only detections sent with a native crop get one. Three phases so that the S3 transfers never
    hold a DB session: read the sequence, cut and upload, then publish all the new keys at once.
    `lease_until` is the lease of the job: nothing is published if another worker took it over.
    """
    async with session_factory() as session:
        sequence_ = await SequenceCRUD(session).get(sequence_id)
        if sequence_ is None or not sequence_.is_validated:
            return
        camera = await CameraCRUD(session).get(sequence_.camera_id)
        if camera is None:
            return
        # ponytail: every detection of the sequence is read on each refresh, fine up to a few thousand
        detections = [
            detection
            for detection in await DetectionCRUD(session).fetch_all(filters=("sequence_id", sequence_id), order_by="id")
            if detection.bbox != EMPTY_BBOXES
        ]
    with_native_crop = [det for det in detections if det.native_crop_bucket_key and det.native_crop_window]
    if not with_native_crop:
        return
    # Stored bboxes hold a single box: "[(xmin,ymin,xmax,ymax,conf)]"
    bboxes = [[float(value) for value in det.bbox.strip("[]()").split(",")] for det in detections]
    union = (
        min(bbox[0] for bbox in bboxes),
        min(bbox[1] for bbox in bboxes),
        max(bbox[2] for bbox in bboxes),
        max(bbox[3] for bbox in bboxes),
    )
    bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(camera.organization_id))

    box = _parse_box(sequence_.crop_box) if sequence_.crop_box else None
    to_crop = [det for det in with_native_crop if det.crop_bucket_key is None]
    if box is None or not _contains(box, union):
        frame_size = await to_thread.run_sync(_frame_size, bucket, with_native_crop)
        if frame_size is None:
            return
        new_box = square_box(union, *frame_size)
        # A region already as large as the frame can't grow: then it never covers the bboxes
        if new_box != box:
            box, to_crop = new_box, with_native_crop
    if not to_crop:
        return
    box_str = f"({','.join(f'{value:.6f}' for value in box)})"

    # Identical crops uploaded within the same second share their key: one a detection already
    # has is not a new object, and must survive the cleanups below.
    current_keys = {det.id: det.crop_bucket_key for det in to_crop}
    new_keys: Dict[int, str] = {}
    try:
        for det in to_crop:
            crop = await to_thread.run_sync(_detection_crop, bucket, det, box)
            if crop is not None:
                new_keys[det.id] = await upload_file(
                    UploadFile(file=io.BytesIO(crop), filename="crop.jpg"),
                    camera.organization_id,
                    camera.id,
                    key_prefix=f"crop_{det.id}_",
                )
    except Exception:
        # The job is retried: don't leave the crops it already uploaded behind
        await delete_objects(
            camera.organization_id, [key for det_id, key in new_keys.items() if key != current_keys[det_id]]
        )
        raise

    async with session_factory() as session:
        sequences, detection_crud = SequenceCRUD(session), DetectionCRUD(session)
        published: Dict[int, str] = {}
        # A worker that outlived its lease read an older sequence than the one that took over
        if lease_until is None or await sequences.holds_crops_lease(sequence_id, lease_until):
            # A detection deleted or moved to another sequence in the meantime keeps what it has
            published = {
                det_id: key
                for det_id, key in new_keys.items()
                if await detection_crud.set_crop(det_id, sequence_id, key)
            }
            if box_str != sequence_.crop_box:
                await sequences.set_crop_box(sequence_id, box_str)
        await session.commit()
        # Objects to delete: the crops that were not published, and the ones that were replaced
        # once no row references them
        unused = [key for det_id, key in new_keys.items() if det_id not in published and key != current_keys[det_id]]
        for det_id, key in published.items():
            replaced = current_keys[det_id]
            if (
                replaced
                and replaced != key
                and not await detection_crud.fetch_all(filters=("crop_bucket_key", replaced), limit=1)
            ):
                unused.append(replaced)
    await delete_objects(camera.organization_id, unused)


async def process_next_due_crops() -> bool:
    """Claim one sequence due for a crop refresh and refresh it. Returns True when a job was claimed."""
    async with session_factory() as session:
        claimed = await SequenceCRUD(session).claim_due_crops(LEASE_SECONDS)
    if claimed is None:
        return False
    sequence_id, due_at, lease_until = claimed
    retry_in_seconds: Optional[float] = None
    try:
        await refresh_sequence_crops(sequence_id, lease_until)
    except Exception:
        logger.exception("Crop refresh failed for sequence %s", sequence_id)
        retry_in_seconds = RETRY_DELAY_SECONDS
    async with session_factory() as session:
        await SequenceCRUD(session).release_crops(sequence_id, due_at, lease_until, retry_in_seconds)
    return True


async def crop_worker_loop() -> None:
    """Per-process crop worker: drains due sequences, then idles on a short poll"""
    logger.info("Crop worker started")
    while True:
        try:
            if not await process_next_due_crops():
                await asyncio.sleep(POLL_SECONDS)
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Crop worker iteration failed; continuing")
            await asyncio.sleep(POLL_SECONDS)
