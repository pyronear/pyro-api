# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime, timedelta
from typing import Annotated, List, cast

from fastapi import APIRouter, Depends, Path, Security, status
from pydantic import PositiveInt
from sqlalchemy import and_, func, select
from sqlalchemy.orm import aliased

from app.api import crud
from app.api.crud.authorizations import check_group_read, check_group_update, is_admin_access
from app.api.crud.groups import get_entity_group_id
from app.api.deps import get_current_access, get_db
from app.db import alerts, events
from app.models import Access, AccessType, Alert, Device, Event, Media
from app.schemas import (
    AccessRead,
    Acknowledgement,
    AcknowledgementOut,
    AlertOut,
    EventIn,
    EventOut,
    EventPayload,
    EventUpdate,
)
from app.services import s3_bucket
from app.services.telemetry import telemetry_client

router = APIRouter(redirect_slashes=True)


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Create a new event")
async def create_event(
    payload: EventIn,
    access: Annotated[AccessRead, Security(get_current_access, scopes=[AccessType.admin, AccessType.device])],
) -> EventOut:
    """Creates a new event based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    telemetry_client.capture(access.id, event="events-create")
    return EventOut(**(await crud.create_entry(events, payload)))


@router.get("/{event_id}/", response_model=EventOut, summary="Get information about a specific event")
async def get_event(
    event_id: int = Path(..., gt=0), requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """
    Based on a event_id, retrieves information about the specified event
    """
    telemetry_client.capture(requester.id, event="events-get", properties={"event_id": event_id})
    requested_group_id = await get_entity_group_id(events, event_id)
    await check_group_read(requester.id, cast(int, requested_group_id))
    return await crud.get_entry(events, event_id)


@router.get("/", response_model=List[EventOut], summary="Get the list of all events")
async def fetch_events(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of all events and their information
    """
    telemetry_client.capture(requester.id, event="events-fetch")
    if await is_admin_access(requester.id):
        return await crud.fetch_all(events)
    else:
        retrieved_events = (
            session.query(Event).join(Alert).join(Device).join(Access).filter(Access.group_id == requester.group_id)
        )
        retrieved_events = [x.__dict__ for x in retrieved_events.all()]
        return retrieved_events


@router.get("/past", response_model=List[EventOut], summary="Get the list of all past events")
async def fetch_past_events(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of all events and their information
    """
    telemetry_client.capture(requester.id, event="events-fetch-past")
    if await is_admin_access(requester.id):
        return await crud.fetch_all(events, exclusions={"end_ts": None})
    else:
        retrieved_events = (
            session.query(Event)
            .join(Alert)
            .join(Device)
            .join(Access)
            .filter(and_(Access.group_id == requester.group_id, Event.end_ts.isnot(None)))
        )
        retrieved_events = [x.__dict__ for x in retrieved_events.all()]
        return retrieved_events


@router.put("/{event_id}/", response_model=EventOut, summary="Update information about a specific event")
async def update_event(
    payload: EventUpdate,
    event_id: int = Path(..., gt=0),
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.device]),
):
    """
    Based on a event_id, updates information about the specified event
    """
    telemetry_client.capture(requester.id, event="events-update", properties={"event_id": event_id})
    requested_group_id = await get_entity_group_id(events, event_id)
    await check_group_update(requester.id, cast(int, requested_group_id))
    return await crud.update_entry(events, payload, event_id)


@router.put("/{event_id}/acknowledge", response_model=AcknowledgementOut, summary="Acknowledge an existing event")
async def acknowledge_event(
    event_id: int = Path(..., gt=0), requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """
    Based on a event_id, acknowledge the specified event
    """
    telemetry_client.capture(requester.id, event="events-acknowledge", properties={"event_id": event_id})
    requested_group_id = await get_entity_group_id(events, event_id)
    await check_group_update(requester.id, cast(int, requested_group_id))
    return await crud.update_entry(events, Acknowledgement(is_acknowledged=True), event_id)


@router.delete("/{event_id}/", response_model=EventOut, summary="Delete a specific event")
async def delete_event(
    event_id: int = Path(..., gt=0),
    access=Security(get_current_access, scopes=[AccessType.admin]),
    session=Depends(get_db),
):
    """
    Based on a event_id, deletes the specified event
    """
    telemetry_client.capture(access.id, event="events-delete", properties={"event_id": event_id})
    return await crud.delete_entry(events, event_id)


@router.get(
    "/unacknowledged",
    response_model=List[EventPayload],
    summary="Get the list of events that haven't been acknowledged",
)
async def fetch_unacknowledged_events(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the last 10 un-acknowledged events and their 10 first alerts
    """
    telemetry_client.capture(requester.id, event="events-fetch-unacnkowledged")
    # Last 10 unacknowledged events
    subquery_events = (
        session
        .query(Event.id)
        .filter(and_(
            Event.is_acknowledged.is_(False),
            Event.created_at > datetime.utcnow() - timedelta(hours=24)
        ))
        .order_by(Event.id.desc())
        .limit(10)
        .subquery()
    )
    if await is_admin_access(requester.id):
        # Alerts associated to the last 10 unacknowledged events
        ranked_alerts = (
            session
            .query(
                Alert.id.label('alert_id'),  # Alias the columns to avoid ambiguity
                Alert.event_id,
                Alert.localization,
                Alert.device_id,
                Alert.media_id,
                func.dense_rank().over(
                    partition_by=Alert.event_id,
                    order_by=Alert.id.asc()
                ).label('rank')
            )
            .filter(Alert.event_id.in_(select([subquery_events.c.id])))
            .subquery()
        )
    else:
        # Limit to devices in the same group
        subquery_devices = (
            session.query(Device.id)
            .join(Access, Device.access_id == Access.id)
            .filter(Access.group_id == requester.group_id)
            .subquery()
        )
        ranked_alerts = (
            session
            .query(
                Alert.id.label('alert_id'),  # Alias the columns to avoid ambiguity
                Alert.event_id,
                Alert.localization,
                Alert.device_id,
                Alert.media_id,
                func.dense_rank().over(
                    partition_by=Alert.event_id,
                    order_by=Alert.id.asc()
                ).label('rank')
            )
            .filter(and_(
                Alert.event_id.in_(select([subquery_events.c.id])),
                Alert.device_id.in_(select([subquery_devices.c.id]))
            ))
            .subquery()
        )
    filtered_alerts = (
        session.query(
            ranked_alerts.c.alert_id,
            ranked_alerts.c.event_id,
            ranked_alerts.c.localization,
            ranked_alerts.c.device_id,
            ranked_alerts.c.media_id
        )
        .filter(ranked_alerts.c.rank <= 10)
        .subquery()
    )
    # Aliased table to allow correct joining without conflicts
    alert_alias = aliased(filtered_alerts)
    # Final query
    retrieved_alerts = (
        session
        .query(
            Event,
            alert_alias.c.alert_id,
            Media.bucket_key,
            alert_alias.c.localization,
            alert_alias.c.device_id,
            Device.login,
            Device.azimuth,
        )
        .join(Event, Event.id == alert_alias.c.event_id)
        .join(Media, Media.id == alert_alias.c.media_id)
        .join(Device, Device.id == alert_alias.c.device_id)
        .distinct()
        .yield_per(100)  # Fetch 100 rows at a time to reduce memory usage
        .all()
    )

    return [
        EventPayload(
            **event.__dict__,
            media_url=await s3_bucket.get_public_url(bucket_key),
            localization=loc,
            device_id=device_id,
            alert_id=alert_id,
            device_login=login,
            device_azimuth=azimuth,
        )
        for event, alert_id, bucket_key, loc, device_id, login, azimuth in retrieved_alerts
    ]


@router.get("/{event_id}/alerts", response_model=List[AlertOut], summary="Get the list of alerts for event")
async def fetch_alerts_for_event(
    event_id: PositiveInt,
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]),
    session=Depends(get_db),
):
    """
    Retrieves the list of alerts associated to the given event and their information
    """
    telemetry_client.capture(requester.id, event="events-fetch-alerts", properties={"event_id": event_id})
    requested_group_id = await get_entity_group_id(events, event_id)
    await check_group_read(requester.id, cast(int, requested_group_id))
    return await crud.base.database.fetch_all(query=alerts.select().where(alerts.c.event_id == event_id))
