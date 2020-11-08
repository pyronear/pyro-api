from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import alerts
from app.api.schemas import AlertOut, AlertIn


router = APIRouter()


@router.post("/", response_model=AlertOut, status_code=201)
async def create_alert(payload: AlertIn):
    return await routing.create_entry(alerts, payload)


@router.get("/{alert_id}/", response_model=AlertOut)
async def get_alert(alert_id: int = Path(..., gt=0)):
    return await routing.get_entry(alerts, alert_id)


@router.get("/", response_model=List[AlertOut])
async def fetch_alerts():
    return await routing.fetch_entries(alerts)


@router.put("/{alert_id}/", response_model=AlertOut)
async def update_alert(payload: AlertIn, alert_id: int = Path(..., gt=0)):
    return await routing.update_entry(alerts, payload, alert_id)


@router.delete("/{alert_id}/", response_model=AlertOut)
async def delete_alert(alert_id: int = Path(..., gt=0)):
    return await routing.delete_entry(alerts, alert_id)
