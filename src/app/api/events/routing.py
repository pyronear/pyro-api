from typing import List
from fastapi import APIRouter, HTTPException, Path
from app.api import crud
from app.db import events
from .schemas import EventIn, EventOut


router = APIRouter()


@router.post("/", response_model=EventOut, status_code=201)
async def create_event(payload: EventIn):
    _id = await crud.post(payload, events)

    return {**payload.dict(), "id": _id}


@router.get("/{id}/", response_model=EventOut)
async def get_event(id: int = Path(..., gt=0),):
    entry = await crud.get(id, events)
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")
    return entry


@router.get("/", response_model=List[EventOut])
async def fetch_events():
    return await crud.fetch_all(events)


@router.put("/{id}/", response_model=EventOut)
async def update_event(payload: EventIn, id: int = Path(..., gt=0),):
    entry = await crud.get(id, events)
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")

    _id = await crud.put(id, payload, events)

    return {**payload.dict(), "id": _id}


@router.delete("/{id}/", response_model=EventOut)
async def delete_event(id: int = Path(..., gt=0)):
    entry = await crud.get(id, events)
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")

    await crud.delete(id, events)

    return entry
