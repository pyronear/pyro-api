# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging

from botocore.exceptions import ClientError

from app.crud import CameraCRUD, DetectionCRUD, PoseCRUD
from app.services.storage import s3_service

__all__ = ["delete_unreferenced_image"]

logger = logging.getLogger("uvicorn.error")


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
    try:
        s3_service.get_bucket(s3_service.resolve_bucket_name(organization_id)).delete_file(bucket_key)
    except ClientError as e:
        # The row already points to the new image: a leftover object is harmless, a failed request is not
        logger.warning(f"Could not delete unreferenced image {bucket_key}: {e}")
