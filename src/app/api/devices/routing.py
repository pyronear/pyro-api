from typing import List
from fastapi import APIRouter, HTTPException, Path
from . import crud
from .schemas import DeviceIn, DeviceOut


router = APIRouter()


@router.post("/", response_model=DeviceOut, status_code=201)
async def create_device(payload: DeviceIn):
    _id = await crud.post(payload)

    return {**payload.dict(), "id": _id}


@router.get("/{id}/", response_model=DeviceOut)
async def get_device(id: int = Path(..., gt=0),):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Device not found")
    return entry


@router.get("/", response_model=List[DeviceOut])
async def fetch_devices():
    return await crud.get_all()


@router.put("/{id}/", response_model=DeviceOut)
async def update_device(payload: DeviceIn, id: int = Path(..., gt=0),):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Device not found")

    _id = await crud.put(id, payload)

    return {**payload.dict(), "id": _id}


@router.delete("/{id}/", response_model=DeviceOut)
async def delete_device(id: int = Path(..., gt=0)):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Device not found")

    await crud.delete(id)

    return entry
