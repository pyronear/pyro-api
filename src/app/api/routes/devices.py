from typing import List
from datetime import datetime
from fastapi import APIRouter, Path, Security, HTTPException

from app.api import crud
from app.db import devices, accesses
from app.api.schemas import (DeviceOut, DeviceAuth, MyDeviceAuth, DeviceCreation, DeviceIn,
                             UserRead, DefaultPosition, Cred)
from app.api.deps import get_current_device, get_current_user

from app.api.routes.accesses import post_access, update_access_pwd

router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=201, summary="Create a new device")
async def create_device(payload: DeviceAuth, _=Security(get_current_user, scopes=["admin"])):
    """Creates a new device based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    access_entry = await post_access(payload.login, payload.password, scopes=payload.scopes)
    return await crud.create_entry(devices, DeviceCreation(**payload.dict(), access_id=access_entry.id))


@router.post("/register", response_model=DeviceOut, status_code=201, summary="Register your device")
async def register_my_device(payload: MyDeviceAuth, me: UserRead = Security(get_current_user, scopes=["admin", "me"])):
    """Creates a new device with the current user being the owner based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    access_entry = await post_access(payload.login, payload.password, scopes=payload.scopes)
    return await crud.create_entry(devices, DeviceCreation(**payload.dict(), owner_id=me.id, access_id=access_entry.id))


@router.get("/{device_id}/", response_model=DeviceOut, summary="Get information about a specific device")
async def get_device(device_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    """
    Based on a device_id, retrieves information about the specified device
    """
    return await crud.get_entry(devices, device_id)


@router.get("/", response_model=List[DeviceOut], summary="Get the list of all devices")
async def fetch_devices(_=Security(get_current_user, scopes=["admin"])):
    """
    Retrieves the list of all devices and their information
    """
    return await crud.fetch_all(devices)


@router.put("/{device_id}/", response_model=DeviceOut, summary="Update information about a specific device")
async def update_device(payload: DeviceIn, device_id: int = Path(..., gt=0)):
    """
    Based on a device_id, updates information about the specified device
    """
    return await crud.update_entry(devices, payload, device_id)


@router.delete("/{device_id}/", response_model=DeviceOut, summary="Delete a specific device")
async def delete_device(device_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    """
    Based on a device_id, deletes the specified device
    """
    entry = await crud.delete_entry(devices, device_id)
    # Delete access
    await crud.delete_entry(accesses, entry['access_id'])
    return entry


@router.get("/my-devices", response_model=List[DeviceOut],
            summary="Get the list of all devices belonging to the current user")
async def fetch_my_devices(me: UserRead = Security(get_current_user, scopes=["admin", "me"])):
    """
    Retrieves the list of all devices and the information which are owned by the current user
    """
    return await crud.fetch_all(devices, {"owner_id": me.id})


@router.put("/heartbeat", response_model=DeviceOut, summary="Update the last ping of the current device")
async def heartbeat(device: DeviceOut = Security(get_current_device, scopes=["device"])):
    """
    Updates the last ping of the current device with the current datetime
    """
    device.last_ping = datetime.utcnow()
    await crud.put(device.id, device, devices)
    return device


@router.put("/{device_id}/location", response_model=DeviceOut, summary="Update the location of a specific device")
async def update_device_location(
    payload: DefaultPosition,
    device_id: int = Path(..., gt=0),
    user: UserRead = Security(get_current_user, scopes=["admin", "me"])
):
    """
    Based on a device_id, updates the location of the specified device
    """
    # Check that device is accessible to this user
    device = await crud.get_entry(devices, device_id)
    if device['owner_id'] != user.id:
        raise HTTPException(
            status_code=400,
            detail="Permission denied"
        )
    # Update only the location
    device.update(payload.dict())
    device = DeviceOut(**device)
    await crud.put(device.id, device, devices)
    return device


@router.put("/my-location", response_model=DeviceOut, summary="Update the location of the current device")
async def update_my_location(
    payload: DefaultPosition,
    device: DeviceOut = Security(get_current_device, scopes=["device"])
):
    """
    Updates the location of the current device
    """
    # Update only the position
    for k, v in payload.dict().items():
        setattr(device, k, v)
    await crud.put(device.id, device, devices)
    return device


@router.put("/{device_id}/pwd", response_model=DeviceOut, summary="Update the password of a specific device")
async def update_device_password(
    payload: Cred,
    device_id: int = Path(..., gt=0),
    _=Security(get_current_user, scopes=["admin"])
):
    """
    Based on a device_id, updates the password of the specified device
    """
    entry = await crud.get_entry(devices, device_id)
    await update_access_pwd(payload, entry["access_id"])
    return entry
