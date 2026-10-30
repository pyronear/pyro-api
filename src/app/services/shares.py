# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from typing import Any, cast

from sqlalchemy import desc
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.time import utcnow
from app.crud import DetectionCRUD
from app.models import Alert, AlertSequence, AlertShare, Camera, Sequence
from app.schemas.shares import (
    SharedAlertRead,
    SharedCameraRead,
    SharedDetectionRead,
    SharedSequenceRead,
    ShareRead,
    ShareStatus,
)
from app.services.storage import s3_service

__all__ = ["build_shared_alert", "serialize_share", "share_status"]

# Bound the public payload: an alert can gather many sequences, each with many frames.
_MAX_SEQUENCES = 20
_MAX_DETECTIONS_PER_SEQUENCE = 10


def share_status(share: AlertShare, now: datetime | None = None) -> ShareStatus:
    if share.revoked_at is not None:
        return ShareStatus.REVOKED
    if share.expires_at <= (now or utcnow()):
        return ShareStatus.EXPIRED
    return ShareStatus.ACTIVE


def serialize_share(share: AlertShare, now: datetime | None = None) -> ShareRead:
    return ShareRead(
        id=share.id,
        alert_id=share.alert_id,
        organization_id=share.organization_id,
        created_by=share.created_by,
        created_at=share.created_at,
        expires_at=share.expires_at,
        revoked_at=share.revoked_at,
        status=share_status(share, now),
    )


async def build_shared_alert(session: AsyncSession, alert: Alert, expires_at: datetime) -> SharedAlertRead:
    """Project an alert onto the fields readable without an account, with short-lived image URLs."""
    seq_stmt: Any = (
        select(Sequence)
        .join(AlertSequence, cast(Any, AlertSequence.sequence_id == Sequence.id))
        .where(AlertSequence.alert_id == alert.id)
        .order_by(desc(cast(Any, Sequence.last_seen_at)))
        .limit(_MAX_SEQUENCES)
    )
    sequences = list((await session.exec(seq_stmt)).all())
    camera_ids = list({sequence.camera_id for sequence in sequences})
    cam_stmt: Any = select(Camera).where(cast(Any, Camera.id).in_(camera_ids))
    cameras = {camera.id: camera for camera in (await session.exec(cam_stmt)).all()}
    detections = await DetectionCRUD(session=session).fetch_latest_with_bbox(
        [sequence.id for sequence in sequences], _MAX_DETECTIONS_PER_SEQUENCE
    )

    shared_sequences = []
    for sequence in sequences:
        camera = cameras[sequence.camera_id]
        # Images live in the bucket of the camera's organization
        bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(camera.organization_id))
        shared_sequences.append(
            SharedSequenceRead(
                started_at=sequence.started_at,
                last_seen_at=sequence.last_seen_at,
                camera_azimuth=sequence.camera_azimuth,
                sequence_azimuth=sequence.sequence_azimuth,
                cone_angle=sequence.cone_angle,
                camera=SharedCameraRead(
                    name=camera.name,
                    lat=camera.lat,
                    lon=camera.lon,
                    elevation=camera.elevation,
                    angle_of_view=camera.angle_of_view,
                ),
                detections=[
                    SharedDetectionRead(
                        recorded_at=detection.recorded_at,
                        bbox=detection.bbox,
                        # A fixed lifetime keeps the URL cache effective (it keys on the expiration)
                        url=bucket.get_public_url(
                            detection.bucket_key, url_expiration=settings.SHARE_URL_EXPIRATION, verify_exists=False
                        ),
                    )
                    for detection in detections.get(sequence.id, [])
                ],
            )
        )

    return SharedAlertRead(
        started_at=alert.started_at,
        last_seen_at=alert.last_seen_at,
        lat=alert.lat,
        lon=alert.lon,
        expires_at=expires_at,
        sequences=shared_sequences,
    )
