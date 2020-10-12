from typing import List
from fastapi import APIRouter, Path, Security

from app.api import routing, crud
from app.db import devices
from app.api.schemas import Device, DeviceOut, DeviceIn, DeviceDBIn, HeartbeatOut, HeartbeatIn
from app.security import get_password_hash
from app.deps import get_current_active_device
from datetime import datetime
from app.api.schemas import DeviceOut, DeviceIn, UserInDb
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=201)
async def create_device(payload: DeviceIn, _=Security(get_current_user, scopes=["admin"])):
    return await routing.create_entry(devices, payload)


@router.get("/{id}/", response_model=DeviceOut)
async def get_device(id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.get_entry(devices, id)


@router.get("/", response_model=List[DeviceOut])
async def fetch_devices(_=Security(get_current_user, scopes=["admin"])):
    return await routing.fetch_entries(devices)


@router.put("/{id}/", response_model=DeviceOut)
async def update_device(payload: DeviceIn, id: int = Path(..., gt=0)):
    # TODO add device auth
    return await routing.update_entry(devices, payload, id)


@router.put("/{id}/heartbeat/", response_model=HeartbeatOut)
async def heartbeat(current_device: Device = Depends(get_current_active_device), id: int = Path(..., gt=0)):
    current_device.last_ping = datetime.utcnow()
    return await routing.update_entry(devices, Device(**current_device), id)
    

@router.delete("/{id}/", response_model=DeviceOut)
async def delete_device(id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.delete_entry(devices, id)


@router.get("/my-devices", response_model=List[DeviceOut])
async def fetch_my_devices(me: UserInDb = Security(get_current_user, scopes=["me"])):
    return await crud.device.fetch_by_owner(owner_id=me.id)
