from typing import List
from fastapi import APIRouter, Path, Security

from app.api import routing
from app.db import devices
from app.api.schemas import DeviceOut, DeviceAuth, DeviceIn, UserRead, HeartbeatOut, DefaultPosition, Cred
from app.api.deps import get_current_device, get_current_user

router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=201)
async def create_device(payload: DeviceAuth, _=Security(get_current_user, scopes=["admin"])):
    return await routing.create_device(devices, payload)


@router.get("/{device_id}/", response_model=DeviceOut)
async def get_device(device_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.get_entry(devices, device_id)


@router.get("/", response_model=List[DeviceOut])
async def fetch_devices(_=Security(get_current_user, scopes=["admin"])):
    return await routing.fetch_entries(devices)


@router.put("/{device_id}/", response_model=DeviceOut)
async def update_device(payload: DeviceIn, device_id: int = Path(..., gt=0)):
    return await routing.update_entry(devices, payload, device_id)


@router.delete("/{device_id}/", response_model=DeviceOut)
async def delete_device(device_id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.delete_entry(devices, device_id)


@router.get("/my-devices", response_model=List[DeviceOut])
async def fetch_my_devices(me: UserRead = Security(get_current_user, scopes=["me"])):
    return await routing.fetch_entries(devices, {"owner_id": me.id})


@router.post("/heartbeat", response_model=HeartbeatOut)
async def heartbeat(device: DeviceOut = Security(get_current_device, scopes=["device"])):
    return await routing.heartbeat(devices, device)


@router.post("/{device_id}/update-location", response_model=DeviceOut)
async def update_location(payload: DefaultPosition,
                          device_id: int = Path(..., gt=0),
                          user: UserRead = Security(get_current_user, scopes=["me"])):
    return await routing.update_location(devices, payload, device_id, user.id)


@router.put("/{device_id}/pwd", response_model=DeviceOut)
async def reset_password(
    payload: Cred,
    device_id: int = Path(..., gt=0),
    _=Security(get_current_user, scopes=["admin"])
):
    return await routing.update_pwd(devices, payload, device_id)
