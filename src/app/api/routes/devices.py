from typing import List
from fastapi import APIRouter, Path, Security

from app.api import routing, crud
from app.db import devices
from app.api.schemas import DeviceOut, DeviceIn, UserRead
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


@router.delete("/{id}/", response_model=DeviceOut)
async def delete_device(id: int = Path(..., gt=0), _=Security(get_current_user, scopes=["admin"])):
    return await routing.delete_entry(devices, id)


@router.get("/my-devices", response_model=List[DeviceOut])
async def fetch_my_devices(me: UserRead = Security(get_current_user, scopes=["me"])):
    return await routing.fetch_entries(devices, ("owner_id", me.id))
