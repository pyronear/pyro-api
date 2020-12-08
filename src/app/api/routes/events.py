from typing import List
from fastapi import APIRouter, Path, Security
from app.api import crud
from app.db import events
from app.api.schemas import EventOut, EventIn
from app.api.deps import get_current_access


router = APIRouter()


@router.post("/", response_model=EventOut, status_code=201, summary="Create a new event")
async def create_event(payload: EventIn, _=Security(get_current_access, scopes=["admin", "device"])):
    """Creates a new event based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(events, payload)


@router.get("/{event_id}/", response_model=EventOut, summary="Get information about a specific event")
async def get_event(event_id: int = Path(..., gt=0)):
    """
    Based on a event_id, retrieves information about the specified event
    """
    return await crud.get_entry(events, event_id)


@router.get("/", response_model=List[EventOut], summary="Get the list of all events")
async def fetch_events():
    """
    Retrieves the list of all events and their information
    """
    return await crud.fetch_all(events)


@router.put("/{event_id}/", response_model=EventOut, summary="Update information about a specific event")
async def update_event(
    payload: EventIn,
    event_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=["admin", "device"])
):
    """
    Based on a event_id, updates information about the specified event
    """
    return await crud.update_entry(events, payload, event_id)


@router.delete("/{event_id}/", response_model=EventOut, summary="Delete a specific event")
async def delete_event(event_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=["admin"])):
    """
    Based on a event_id, deletes the specified event
    """
    return await crud.delete_entry(events, event_id)
