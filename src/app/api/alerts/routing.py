from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.api import crud
from app.db import alerts
from .schemas import AlertIn, AlertOut


router = APIRouter()


@router.post("/", response_model=AlertOut, status_code=201)
async def create_alert(payload: AlertIn):
    _id = await crud.post(payload, alerts)

    return {**payload.dict(), "id": _id}


@router.get("/{id}/", response_model=AlertOut)
async def get_alert(id: int = Path(..., gt=0),):
    entry = await crud.get(id, alerts)
    if not entry:
        raise HTTPException(status_code=404, detail="Alert not found")
    return entry


@router.get("/", response_model=List[AlertOut])
async def fetch_alerts():
    return await crud.fetch_all(alerts)


@router.put("/{id}/", response_model=AlertOut)
async def update_alert(payload: AlertIn, id: int = Path(..., gt=0),):
    entry = await crud.get(id, alerts)
    if not entry:
        raise HTTPException(status_code=404, detail="Alert not found")

    _id = await crud.put(id, payload, alerts)

    return {**payload.dict(), "id": _id}


@router.delete("/{id}/", response_model=AlertOut)
async def delete_alert(id: int = Path(..., gt=0)):
    entry = await crud.get(id, alerts)
    if not entry:
        raise HTTPException(status_code=404, detail="Alert not found")

    await crud.delete(id, alerts)

    return entry
