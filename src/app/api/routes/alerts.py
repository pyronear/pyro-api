# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from functools import partial
from typing import List, cast

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Path, Security, status
from sqlalchemy import select

from app.api import crud
from app.api.crud.authorizations import check_group_read, is_admin_access
from app.api.crud.groups import get_entity_group_id
from app.api.deps import get_current_access, get_current_device
from app.api.external import post_request
from app.api.schemas import AlertBase, AlertIn, AlertOut, DeviceOut
from app.db import alerts, events, get_session, media, models
from app.db.models import AccessType

router = APIRouter()


async def check_media_existence(media_id):
    existing_media = await crud.get(media_id, media)
    if existing_media is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Unable to find media with id={media_id}.")


async def alert_notification(payload: AlertOut):
    # Fetch URLs that required POST upon route completion
    webhook_urls = await crud.webhooks.fetch_webhook_urls("create_alert")
    # Post the payload to each URL
    map(partial(post_request, payload=payload), webhook_urls)


@router.post("/", response_model=AlertOut, status_code=status.HTTP_201_CREATED, summary="Create a new alert")
async def create_alert(
    payload: AlertIn,
    background_tasks: BackgroundTasks,
    _=Security(get_current_access, scopes=[AccessType.admin]),
):
    """
    Creates a new alert based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """

    if payload.media_id is not None:
        await check_media_existence(payload.media_id)

    if payload.event_id is None:
        payload.event_id = await crud.alerts.create_event_if_inexistant(payload)
    alert = await crud.create_entry(alerts, payload)
    # Send notification
    background_tasks.add_task(alert_notification, alert)
    return alert


@router.post(
    "/from-device",
    response_model=AlertOut,
    status_code=status.HTTP_201_CREATED,
    summary="Create an alert related to the authentified device",
)
async def create_alert_from_device(
    payload: AlertBase,
    background_tasks: BackgroundTasks,
    device: DeviceOut = Security(get_current_device, scopes=[AccessType.device]),
):
    """
    Creates an alert related to the authentified device, uses its device_id as argument

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    payload_dict = payload.dict()
    # If no azimuth is specified, use the one from the device
    payload_dict["azimuth"] = payload_dict["azimuth"] if isinstance(payload_dict["azimuth"], float) else device.azimuth
    return await create_alert(AlertIn(**payload_dict, device_id=device.id), background_tasks)


@router.get("/{alert_id}/", response_model=AlertOut, summary="Get information about a specific alert")
async def get_alert(
    alert_id: int = Path(..., gt=0), requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """
    Based on a alert_id, retrieves information about the specified alert
    """
    requested_group_id = await get_entity_group_id(alerts, alert_id)
    await check_group_read(requester.id, cast(int, requested_group_id))
    return await crud.get_entry(alerts, alert_id)


@router.get("/", response_model=List[AlertOut], summary="Get the list of all alerts")
async def fetch_alerts(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_session)
):
    """
    Retrieves the list of all alerts and their information
    """
    if await is_admin_access(requester.id):
        return await crud.fetch_all(alerts)
    else:
        retrieved_alerts = (
            session.query(models.Alerts)
            .join(models.Devices)
            .join(models.Accesses)
            .filter(models.Accesses.group_id == requester.group_id)
            .all()
        )
        retrieved_alerts = [x.__dict__ for x in retrieved_alerts]
        return retrieved_alerts


@router.delete("/{alert_id}/", response_model=AlertOut, summary="Delete a specific alert")
async def delete_alert(alert_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Based on a alert_id, deletes the specified alert
    """
    return await crud.delete_entry(alerts, alert_id)


@router.get("/ongoing", response_model=List[AlertOut], summary="Get the list of ongoing alerts")
async def fetch_ongoing_alerts(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_session)
):
    """
    Retrieves the list of ongoing alerts and their information
    """

    if await is_admin_access(requester.id):
        query = (
            alerts.select().where(alerts.c.event_id.in_(select([events.c.id]).where(events.c.end_ts.is_(None))))
        ).order_by(alerts.c.id.desc())

        return (await crud.base.database.fetch_all(query=query.limit(50)))[::-1]
    else:
        retrieved_alerts = (
            session.query(models.Alerts)
            .join(models.Events)
            .filter(models.Events.end_ts.is_(None))
            .join(models.Devices)
            .join(models.Accesses)
            .filter(models.Accesses.group_id == requester.group_id)
        )
        retrieved_alerts = [x.__dict__ for x in retrieved_alerts.all()]
        return retrieved_alerts
