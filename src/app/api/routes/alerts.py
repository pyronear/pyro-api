from typing import List
from fastapi import APIRouter, Path, Security, HTTPException
from app.api import crud
from app.db import alerts, AlertType, media
from app.api.schemas import AlertBase, AlertOut, AlertIn, AlertMediaId, DeviceOut
from app.api.deps import get_current_device


router = APIRouter()


async def check_media_existence(media_id):
    existing_media = await crud.get(media_id, media)
    if existing_media is None:
        raise HTTPException(
            status_code=404,
            detail="Media does not exist"
        )


@router.post("/", response_model=AlertOut, status_code=201, summary="Create a new alert")
async def create_alert(payload: AlertIn):
    """
    Creates a new alert based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
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
async def get_alert(alert_id: int = Path(..., gt=0)):
    """
    Based on a alert_id, retrieves information about the specified alert
    """
    return await crud.get_entry(alerts, alert_id)


@router.get("/", response_model=List[AlertOut], summary="Get the list of all alerts")
async def fetch_alerts():
    """
    Retrieves the list of all alerts and their information
    """
    return await crud.fetch_all(alerts)


@router.put("/{alert_id}/", response_model=AlertOut, summary="Update information about a specific alert")
async def update_alert(payload: AlertIn, alert_id: int = Path(..., gt=0)):
    """
    Based on a alert_id, updates information about the specified alert
    """
    return await crud.update_entry(alerts, payload, alert_id)


@router.delete("/{alert_id}/", response_model=AlertOut)
async def delete_alert(alert_id: int = Path(..., gt=0), summary="Delete a specific alert"):
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
            status_code=400,
            detail="Permission denied"
        )

    await check_media_existence(payload.media_id)
    existing_alert = dict(**existing_alert)
    existing_alert["media_id"] = payload.media_id
    return await crud.update_entry(alerts, AlertIn(**existing_alert), alert_id)


@router.get("/ongoing", response_model=List[AlertOut], summary="Get the list of ongoing alerts")
async def fetch_ongoing_alerts():
    """
    Retrieves the list of ongoing alerts and their information
    """
    return await crud.fetch_ongoing_alerts(alerts, {"type": AlertType.start},
                                           excluded_events_filter={"type": AlertType.end})


@router.get("/unacknowledged", response_model=List[AlertOut], summary="Get the list of non confirmed alerts")
async def fetch_unacknowledged_alerts():
    """
    Retrieves the list of non confirmed alerts and their information
    """
    return await crud.fetch_all(alerts, {"is_acknowledged": False})
