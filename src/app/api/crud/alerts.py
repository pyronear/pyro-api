# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime, timedelta
from typing import Any, Dict, List, Mapping, Optional

from sqlalchemy import Table, and_

import app.config as cfg
from app.api import crud
from app.api.routes.events import create_event
from app.api.schemas import AlertIn, AlertOut, EventIn
from app.db import alerts


async def fetch_ongoing_alerts(
    table: Table, query_filters: Dict[str, Any], excluded_events_filter: Dict[str, Any], limit: int = 50,
) -> List[Mapping[str, Any]]:
    query = table.select().order_by(table.c.id.desc())
    if isinstance(query_filters, dict):
        for query_filter_key, query_filter_value in query_filters.items():
            query = query.where(getattr(table.c, query_filter_key) == query_filter_value)

    #  TODO Should be performed using a sqlalchemy accessor. E.g: alert_event_end_ts is None
    all_closed_events = table.select().with_only_columns([table.c.event_id])
    if isinstance(excluded_events_filter, dict):
        for query_filter_key, query_filter_value in excluded_events_filter.items():
            all_closed_events = all_closed_events.where(getattr(table.c, query_filter_key) == query_filter_value)
    query = query.where(~getattr(table.c, "event_id").in_(all_closed_events))

    return await crud.base.database.fetch_all(query=query.limit(limit).order_by(table.c.id.asc()))


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
