from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import devices
from app.api.schemas import DeviceOut, DeviceIn


router = APIRouter()

@router.post("/", response_model=DeviceOut, status_code=201)
async def create_device(payload: DeviceIn):
    return await routing.create_entry(devices, payload)


@router.get("/{id}/", response_model=DeviceOut)
async def get_device(id: int = Path(..., gt=0)):
    return await routing.get_entry(devices, id)


@router.get("/", response_model=List[DeviceOut])
async def fetch_devices():
    return await routing.fetch_entries(devices)


@router.put("/{id}/", response_model=DeviceOut)
async def update_device(payload: DeviceIn, id: int = Path(..., gt=0)):
    return await routing.update_entry(devices, payload, id)


@router.delete("/{id}/", response_model=DeviceOut)
async def delete_device(id: int = Path(..., gt=0)):
    return await routing.delete_entry(devices, id)
