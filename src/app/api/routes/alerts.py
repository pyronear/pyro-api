# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List
from fastapi import APIRouter, Path, Security, HTTPException, status
from sqlalchemy import select, and_
from datetime import datetime, timedelta

from app.api import crud
from app.db import alerts, events, media
from app.api.schemas import AlertBase, AlertOut, AlertIn, AlertMediaId, DeviceOut, Ackowledgement, AcknowledgementOut, EventIn
from app.api.deps import get_current_device, get_current_access
from app.api.routes.events import create_event


router = APIRouter()


async def check_media_existence(media_id):
    existing_media = await crud.get(media_id, media)
    if existing_media is None:
        raise HTTPException(
            status_code=404,
            detail="Media does not exist"
        )


@router.post("/", response_model=AlertOut, status_code=201, summary="Create a new alert")
async def create_alert(payload: AlertIn, _=Security(get_current_access, scopes=["admin"])):
    """
    Creates a new alert based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """

    if payload.event_id is None:
        # check whether there is an alert in the last 5 min by the same device
        max_ts = datetime.utcnow() - timedelta(minutes=5)
        query = (
            alerts.select()
            .where(
                and_(
                    alerts.c.device_id == payload.device_id,
                    alerts.c.created_at >= max_ts
                )
            )
            .limit(1)
        )

        previous_alert = await crud.base.database.fetch_all(query=query)
        if len(previous_alert) == 0:
            # Create an event & get the ID
            event = await create_event(EventIn(lat=payload.lat, lon=payload.lon, start_ts=datetime.utcnow()))
            event_id = event['id']
        # Get event ref
        else:
            event_id = previous_alert[0]['event_id']
        payload.event_id = event_id


    if payload.media_id is not None:
        await check_media_existence(payload.media_id)
    return await crud.create_entry(alerts, payload)


@router.post("/from-device", response_model=AlertOut, status_code=201,
             summary="Create an alert related to the authentified device")
async def create_alert_from_device(payload: AlertBase,
                                   device: DeviceOut = Security(get_current_device, scopes=["device"])):
    """
    Creates an alert related to the authentified device, uses its device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    if payload.media_id is not None:
        await check_media_existence(payload.media_id)
    return await crud.create_entry(alerts, AlertIn(**payload.dict(), device_id=device.id))


@router.get("/{alert_id}/", response_model=AlertOut, summary="Get information about a specific alert")
async def get_alert(alert_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=["admin"])):
    """
    Based on a alert_id, retrieves information about the specified alert
    """
    return await crud.get_entry(alerts, alert_id)


@router.get("/", response_model=List[AlertOut], summary="Get the list of all alerts")
async def fetch_alerts(_=Security(get_current_access, scopes=["admin"])):
    """
    Retrieves the list of all alerts and their information
    """
    return await crud.fetch_all(alerts)


@router.put("/{alert_id}/", response_model=AlertOut, summary="Update information about a specific alert")
async def update_alert(
    payload: AlertIn,
    alert_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=["admin"])
):
    """
    Based on a alert_id, updates information about the specified alert
    """
    return await crud.update_entry(alerts, payload, alert_id)


@router.put("/{alert_id}/acknowledge", response_model=AcknowledgementOut, summary="Acknowledge an existing alert")
async def acknowledge_alert(alert_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=["admin"])):
    """
    Based on a alert_id, acknowledge the specified alert
    """
    return await crud.update_entry(alerts, Ackowledgement(is_acknowledged=True), alert_id)


@router.delete("/{alert_id}/", response_model=AlertOut, summary="Delete a specific alert")
async def delete_alert(alert_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=["admin"])):
    """
    Based on a alert_id, deletes the specified alert
    """
    return await crud.delete_entry(alerts, alert_id)


@router.put("/{alert_id}/link-media", response_model=AlertOut, summary="Link an alert to a media")
async def link_media(payload: AlertMediaId,
                     alert_id: int = Path(..., gt=0),
                     current_device: DeviceOut = Security(get_current_device, scopes=["device"])):
    """
    Based on a alert_id, and media information as arguments, link the specified alert to a media
    """
    # Check that alert is linked to this device
    existing_alert = await crud.fetch_one(alerts, {"id": alert_id, "device_id": current_device.id})
    if existing_alert is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Permission denied"
        )

    await check_media_existence(payload.media_id)
    existing_alert = dict(**existing_alert)
    existing_alert["media_id"] = payload.media_id
    return await crud.update_entry(alerts, AlertIn(**existing_alert), alert_id)


@router.get("/ongoing", response_model=List[AlertOut], summary="Get the list of ongoing alerts")
async def fetch_ongoing_alerts(_=Security(get_current_access, scopes=["admin"])):
    """
    Retrieves the list of ongoing alerts and their information
    """
    query = (
        alerts.select()
        .where(
            alerts.c.event_id.in_(
                select([events.c.id])
                .where(events.c.end_ts.isnot(None))
            )
        )
    )

    return await crud.base.database.fetch_all(query=query)


@router.get("/unacknowledged", response_model=List[AlertOut], summary="Get the list of non confirmed alerts")
async def fetch_unacknowledged_alerts(_=Security(get_current_access, scopes=["admin"])):
    """
    Retrieves the list of non confirmed alerts and their information
    """
    return await crud.fetch_all(alerts, {"is_acknowledged": False})
