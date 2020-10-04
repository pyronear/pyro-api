from typing import List
from fastapi import APIRouter, HTTPException, Path
from . import crud
from .schemas import EventIn, EventOut


router = APIRouter()


@router.post("/", response_model=EventOut, status_code=201)
async def create_event(payload: EventIn):
    _id = await crud.post(payload)

    return {**payload.dict(), "id": _id}


@router.get("/{id}/", response_model=EventOut)
async def get_event(id: int = Path(..., gt=0),):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")
    return entry


@router.get("/", response_model=List[EventOut])
async def fetch_events():
    return await crud.get_all()


@router.put("/{id}/", response_model=EventOut)
async def update_event(payload: EventIn, id: int = Path(..., gt=0),):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")

    _id = await crud.put(id, payload)

    return {**payload.dict(), "id": _id}


@router.delete("/{id}/", response_model=EventOut)
async def delete_event(id: int = Path(..., gt=0)):
    entry = await crud.get(id)
    if not entry:
        raise HTTPException(status_code=404, detail="Event not found")

    await crud.delete(id)

    return entry
