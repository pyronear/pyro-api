from typing import List
from fastapi import APIRouter, Path, Security, HTTPException
from app.api import crud
from app.db import alerts, AlertType, media
from app.api.schemas import AlertBase, AlertOut, AlertIn, AlertMediaId, DeviceOut
from app.api.deps import get_current_device


router = APIRouter()


@router.post("/", response_model=AlertOut, status_code=201)
async def create_alert(payload: AlertIn):
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
    return await crud.create_entry(alerts, AlertIn(**payload.dict(), device_id=device.id))


@router.get("/{alert_id}/", response_model=AlertOut)
async def get_alert(alert_id: int = Path(..., gt=0)):
    return await crud.get_entry(alerts, alert_id)


@router.get("/", response_model=List[AlertOut])
async def fetch_alerts():
    return await crud.fetch_all(alerts)


@router.put("/{alert_id}/", response_model=AlertOut)
async def update_alert(payload: AlertIn, alert_id: int = Path(..., gt=0)):
    return await crud.update_entry(alerts, payload, alert_id)


@router.delete("/{alert_id}/", response_model=AlertOut)
async def delete_alert(alert_id: int = Path(..., gt=0)):
    return await crud.delete_entry(alerts, alert_id)


@router.put("/{alert_id}/link-media", response_model=AlertOut)
async def link_media(payload: AlertMediaId,
                     alert_id: int = Path(..., gt=0),
                     current_device: DeviceOut = Security(get_current_device, scopes=["device"])):
    # Check that alert is linked to this device
    existing_alert = await crud.fetch_one(alerts, {"id": alert_id, "device_id": current_device.id})
    if existing_alert is None:
        raise HTTPException(
            status_code=400,
            detail="Permission denied"
        )
    
    existing_media = await crud.fetch_one(media, {"id": payload.media_id})
    if existing_media is None:
        raise HTTPException(
            status_code=404,
            detail="Media does not exist"
        )
    existing_alert = dict(**existing_alert)
    existing_alert["media_id"] = payload.media_id
    return await crud.update_entry(alerts, AlertIn(**existing_alert), alert_id)


@router.get("/ongoing", response_model=List[AlertOut])
async def fetch_ongoing_alerts():
    return await crud.fetch_ongoing_alerts(alerts, {"type": AlertType.start},
                                           excluded_events_filter={"type": AlertType.end})


@router.get("/unacknowledged", response_model=List[AlertOut])
async def fetch_unacknowledged_alerts():
    return await crud.fetch_all(alerts, {"is_acknowledged": False})
