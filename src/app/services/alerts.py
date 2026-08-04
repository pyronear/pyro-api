# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import Any, NamedTuple, cast

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud import AlertCRUD
from app.models import AlertSequence, Camera, Sequence
from app.schemas.alerts import AlertUpdate
from app.services.inference import inference_service

__all__ = ["AlertRefresh", "apply_alert_refresh", "plan_alert_refresh", "refresh_alert_state"]


class AlertRefresh(NamedTuple):
    alert_id: int
    update: AlertUpdate | None


async def plan_alert_refresh(
    alert_id: int, session: AsyncSession, exclude_sequence_id: int | None = None
) -> AlertRefresh:
    """Compute an alert refresh without mutating the database."""
    remaining_stmt: Any = (
        select(Sequence, Camera)
        .join(AlertSequence, cast(Any, AlertSequence.sequence_id) == Sequence.id)
        .join(Camera, cast(Any, Camera.id) == Sequence.camera_id)
    )
    remaining_stmt = remaining_stmt.where(AlertSequence.alert_id == alert_id)
    if exclude_sequence_id is not None:
        remaining_stmt = remaining_stmt.where(Sequence.id != exclude_sequence_id)
    remaining_res = await session.exec(remaining_stmt)
    rows = remaining_res.all()
    if not rows:
        return AlertRefresh(alert_id, None)

    seqs = [row[0] for row in rows]
    cams = [row[1] for row in rows]
    new_start = min(seq.started_at for seq in seqs)
    new_last = max(seq.last_seen_at for seq in seqs)

    loc: tuple[float, float] | None = None
    if len(rows) >= 2:
        records = []
        for seq, cam in zip(seqs, cams, strict=False):
            records.append({
                "id": seq.id,
                "pose_id": seq.pose_id,
                "lat": cam.lat,
                "lon": cam.lon,
                "sequence_azimuth": seq.sequence_azimuth,
                "cone_angle": seq.cone_angle,
                "is_wildfire": seq.is_wildfire,
                "started_at": seq.started_at,
                "last_seen_at": seq.last_seen_at,
            })
        groups = await inference_service.triangulate(records)
        loc = next((group.smoke_location for group in groups if group.smoke_location is not None), None)

    return AlertRefresh(
        alert_id,
        AlertUpdate(
            started_at=new_start,
            last_seen_at=new_last,
            lat=loc[0] if loc else None,
            lon=loc[1] if loc else None,
        ),
    )


async def apply_alert_refresh(refresh: AlertRefresh, alerts: AlertCRUD) -> None:
    if refresh.update is None:
        await alerts.delete(refresh.alert_id)
    else:
        await alerts.update(refresh.alert_id, refresh.update)


async def refresh_alert_state(alert_id: int, session: AsyncSession, alerts: AlertCRUD) -> None:
    """Recompute an alert's bounds and location from its remaining sequences, or delete it if empty."""
    await apply_alert_refresh(await plan_alert_refresh(alert_id, session), alerts)
