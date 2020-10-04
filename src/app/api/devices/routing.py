from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.api import crud
from app.db import devices
from .schemas import DeviceIn, DeviceOut


router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=201)
async def create_device(payload: DeviceIn):
    _id = await crud.post(payload, devices)

    return {**payload.dict(), "id": _id}


@router.get("/{id}/", response_model=DeviceOut)
async def get_device(id: int = Path(..., gt=0),):
    entry = await crud.get(id, devices)
    if not entry:
        raise HTTPException(status_code=404, detail="Device not found")
    return entry


@router.get("/", response_model=List[DeviceOut])
async def fetch_devices():
    return await crud.fetch_all(devices)


@router.put("/{id}/", response_model=DeviceOut)
async def update_device(payload: DeviceIn, id: int = Path(..., gt=0),):
    entry = await crud.get(id, devices)
    if not entry:
        raise HTTPException(status_code=404, detail="Device not found")

    _id = await crud.put(id, payload, devices)

    return {**payload.dict(), "id": _id}


@router.delete("/{id}/", response_model=DeviceOut)
async def delete_device(id: int = Path(..., gt=0)):
    entry = await crud.get(id, devices)
    if not entry:
        raise HTTPException(status_code=404, detail="Device not found")

    await crud.delete(id, devices)

    return entry
