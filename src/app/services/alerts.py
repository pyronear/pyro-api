# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import Any, Union, cast

import pandas as pd
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud import AlertCRUD
from app.models import AlertSequence, Camera, Sequence
from app.schemas.alerts import AlertUpdate
from app.services.overlap import compute_overlap

__all__ = ["refresh_alert_state"]


async def refresh_alert_state(alert_id: int, session: AsyncSession, alerts: AlertCRUD) -> None:
    """Recompute an alert's bounds and location from its remaining sequences, or delete it if empty."""
    remaining_stmt: Any = (
        select(Sequence, Camera)
        .join(AlertSequence, cast(Any, AlertSequence.sequence_id) == Sequence.id)
        .join(Camera, cast(Any, Camera.id) == Sequence.camera_id)
    )
    remaining_stmt = remaining_stmt.where(AlertSequence.alert_id == alert_id)
    remaining_res = await session.exec(remaining_stmt)
    rows = remaining_res.all()
    if not rows:
        await alerts.delete(alert_id)
        return

    seqs = [row[0] for row in rows]
    cams = [row[1] for row in rows]
    new_start = min(seq.started_at for seq in seqs)
    new_last = max(seq.last_seen_at for seq in seqs)

    loc: Union[tuple[float, float], None] = None
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
        df = compute_overlap(pd.DataFrame.from_records(records))
        loc = next((loc for locs in df["event_smoke_locations"].tolist() for loc in locs if loc is not None), None)

    await alerts.update(
        alert_id,
        AlertUpdate(
            started_at=new_start,
            last_seen_at=new_last,
            lat=loc[0] if loc else None,
            lon=loc[1] if loc else None,
        ),
    )
