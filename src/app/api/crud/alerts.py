# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy import and_

import app.config as cfg
from app.api import crud
from app.api.routes.events import create_event
from app.api.schemas import AlertIn, AlertOut, EventIn
from app.db import alerts


async def resolve_previous_alert(device_id: int) -> Optional[AlertOut]:
    # check whether there is an alert in the last 5 min by the same device
    max_ts = datetime.utcnow() - timedelta(seconds=cfg.ALERT_RELAXATION_SECONDS)
    query = (
        alerts.select()
        .where(
            and_(
                alerts.c.device_id == device_id,
                alerts.c.created_at >= max_ts
            )
        )
        .order_by(alerts.c.created_at.desc())
        .limit(1)
    )

    entries = await crud.base.database.fetch_all(query=query)

    return entries[0] if len(entries) > 0 else None


async def create_event_if_inexistant(payload: AlertIn) -> int:
    # check whether there is an alert in the last 5 min by the same device
    previous_alert = await resolve_previous_alert(payload.device_id)
    if previous_alert is None:
        # Create an event & get the ID
        event = await create_event(EventIn(lat=payload.lat, lon=payload.lon, start_ts=datetime.utcnow()))
        event_id = event['id']
    # Get event ref
    else:
        event_id = previous_alert['event_id']
    return event_id
