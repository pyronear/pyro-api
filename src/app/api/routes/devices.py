from typing import List
from datetime import datetime
from fastapi import APIRouter, Path, Security, HTTPException

from app.api import crud
from app.db import devices
from app.api.schemas import DeviceOut, DeviceAuth, DeviceCreation, DeviceIn, UserRead, DefaultPosition, Cred
from app.api.deps import get_current_device, get_current_user

from app.api.routes.accesses import post_access, update_access_pwd

router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=201)
async def create_device(payload: DeviceAuth, _=Security(get_current_user, scopes=["admin"])):
    access_entry = await post_access(payload.name, payload.password, scopes=payload.scopes)
    return await crud.create_entry(devices, DeviceCreation(**payload.dict(), access_id=access_entry.id))


@router.get("/{device_id}/", response_model=DeviceOut)
async def get_device(device_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await crud.get_entry(devices, device_id)


@router.get("/", response_model=List[DeviceOut])
async def fetch_devices(_=Security(get_current_user, scopes=["admin"])):
    return await crud.fetch_all(devices)


@router.put("/{device_id}/", response_model=DeviceOut)
async def update_device(payload: DeviceIn, device_id: int = Path(..., gt=0)):
    return await crud.update_entry(devices, payload, device_id)


@router.delete("/{device_id}/", response_model=DeviceOut)
async def delete_device(device_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await crud.delete_entry(devices, device_id)


@router.get("/my-devices", response_model=List[DeviceOut])
async def fetch_my_devices(me: UserRead = Security(get_current_user, scopes=["me"])):
    return await crud.fetch_all(devices, [("owner_id", me.id)])


@router.put("/heartbeat", response_model=DeviceOut)
async def heartbeat(device: DeviceOut = Security(get_current_device, scopes=["device"])):
    device.last_ping = datetime.utcnow()
    await crud.put(device.id, device, devices)
    return device


@router.put("/{device_id}/location", response_model=DeviceOut)
async def update_device_location(
    payload: DefaultPosition,
    device_id: int = Path(..., gt=0),
    user: UserRead = Security(get_current_user, scopes=["me"])
):
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


@router.put("/my-location", response_model=DeviceOut)
async def update_my_location(
    payload: DefaultPosition,
    device: DeviceOut = Security(get_current_device, scopes=["device"])
):
    # Update only the position
    for k, v in payload.dict().items():
        setattr(device, k, v)
    await crud.put(device.id, device, devices)
    return device


@router.put("/{device_id}/pwd", response_model=DeviceOut)
async def update_device_password(
    payload: Cred,
    device_id: int = Path(..., gt=0),
    _=Security(get_current_user, scopes=["admin"])
):
    entry = await crud.get_entry(devices, device_id)
    await update_access_pwd(payload, entry["access_id"])
    return entry
