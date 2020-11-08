from typing import List
from fastapi import APIRouter, Path
from app.api import routing
from app.db import events
from app.api.schemas import EventOut, EventIn


router = APIRouter()


@router.post("/", response_model=EventOut, status_code=201)
async def create_event(payload: EventIn):
    return await routing.create_entry(events, payload)


@router.get("/{event_id}/", response_model=EventOut)
async def get_event(event_id: int = Path(..., gt=0)):
    return await routing.get_entry(events, event_id)


@router.get("/", response_model=List[EventOut])
async def fetch_events():
    return await routing.fetch_entries(events)


@router.put("/{event_id}/", response_model=EventOut)
async def update_event(payload: EventIn, event_id: int = Path(..., gt=0)):
    return await routing.update_entry(events, payload, event_id)


@router.delete("/{event_id}/", response_model=EventOut)
async def delete_event(event_id: int = Path(..., gt=0)):
    return await routing.delete_entry(events, event_id)
