from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import alerts
from app.api.schemas import AlertOut, AlertIn


router = APIRouter()


@router.post("/", response_model=AlertOut, status_code=201)
async def create_alert(payload: AlertIn):
    return await routing.create_entry(alerts, payload)


@router.get("/{id}/", response_model=AlertOut)
async def get_alert(id: int = Path(..., gt=0)):
    return await routing.get_entry(alerts, id)


@router.get("/", response_model=List[AlertOut])
async def fetch_alerts():
    return await routing.fetch_entries(alerts)


@router.put("/{id}/", response_model=AlertOut)
async def update_alert(payload: AlertIn, id: int = Path(..., gt=0)):
    return await routing.update_entry(alerts, payload, id)


@router.delete("/{id}/", response_model=AlertOut)
async def delete_alert(id: int = Path(..., gt=0)):
    return await routing.delete_entry(alerts, id)
