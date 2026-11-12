# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging
from typing import Iterable

from anyio import to_thread
from botocore.exceptions import BotoCoreError, ClientError

from app.crud import CameraCRUD, DetectionCRUD, PoseCRUD
from app.services.storage import s3_service

__all__ = ["delete_unreferenced_crop", "delete_unreferenced_image", "delete_unreferenced_objects"]

logger = logging.getLogger("uvicorn.error")


def _delete_object(organization_id: int, bucket_key: str) -> None:
    try:
        s3_service.get_bucket(s3_service.resolve_bucket_name(organization_id)).delete_file(bucket_key)
    except (ClientError, BotoCoreError, ValueError) as e:
        # The row is already committed: a leftover object is harmless, a failed request is not.
        # ValueError: S3Bucket raises it when a bucket that is not cached yet can't be reached.
        logger.warning(f"Could not delete unreferenced object {bucket_key}: {e}")


async def delete_unreferenced_image(
    organization_id: int,
    bucket_key: str,
    cameras: CameraCRUD,
    poses: PoseCRUD,
    detections: DetectionCRUD,
) -> None:
    """Delete an image object once no camera, pose or detection references its key, to call after the row update"""
    # A key only depends on the camera, the upload second and the content: the same frame sent as last image,
    # pose image or detection frame within one second is one object
    if (
        await cameras.fetch_all(filters=("last_image", bucket_key), limit=1)
        or await poses.fetch_all(filters=("image", bucket_key), limit=1)
        or await detections.fetch_all(filters=("bucket_key", bucket_key), limit=1)
    ):
        return
    _delete_object(organization_id, bucket_key)


async def delete_unreferenced_crop(organization_id: int, crop_bucket_key: str, detections: DetectionCRUD) -> None:
    """Delete a crop object once no detection references its key, to call after the row deletion"""
    # Same key format, with a crop prefix: only another crop can share it
    if not await detections.fetch_all(filters=("crop_bucket_key", crop_bucket_key), limit=1):
        _delete_object(organization_id, crop_bucket_key)


async def delete_unreferenced_objects(
    organization_id: int,
    bucket_keys: Iterable[str],
    cameras: CameraCRUD,
    poses: PoseCRUD,
    detections: DetectionCRUD,
) -> None:
    """Delete the objects of many keys (images and crops), except those a camera, pose or detection still references,
    to call after the rows are deleted"""
    keys = sorted(set(bucket_keys))
    unreferenced = []
    # Checked in chunks, with one query per column, instead of three queries per key
    for start in range(0, len(keys), 1000):
        chunk = keys[start : start + 1000]
        referenced = {cam.last_image for cam in await cameras.get_in(chunk, "last_image")}
        referenced |= {pose.image for pose in await poses.get_in(chunk, "image")}
        for det in await detections.get_in(chunk, "bucket_key") + await detections.get_in(chunk, "crop_bucket_key"):
            referenced |= {det.bucket_key, det.crop_bucket_key}
        unreferenced.extend(key for key in chunk if key not in referenced)
    if not unreferenced:
        return
    try:
        bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(organization_id))
        await to_thread.run_sync(bucket.delete_files, unreferenced)
    except (ClientError, BotoCoreError, ValueError) as e:
        # The rows are already committed: leftover objects are harmless, a failed request is not
        logger.warning(f"Could not delete {len(unreferenced)} unreferenced objects: {e}")
