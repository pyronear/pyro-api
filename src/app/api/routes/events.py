# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List
from fastapi import APIRouter, Path, Security, status, HTTPException
from app.api import crud
from app.db import events
from app.api.schemas import EventOut, EventIn, AccessType
from app.api.deps import get_current_access

router = APIRouter()


@router.post("/", response_model=EventOut, status_code=201, summary="Create a new event")
async def create_event(payload: EventIn, _=Security(get_current_access, scopes=[AccessType.admin, AccessType.device])):
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
    # TODO: would need to check the group from the device entry
    return await crud.get_entry(events, event_id)


@router.get("/", response_model=List[EventOut], summary="Get the list of all events")
async def fetch_events():
    """
    Retrieves the list of all events and their information
    """
    # TODO fetch only group
    return await crud.fetch_all(events)


@router.get("/past", response_model=List[EventOut], summary="Get the list of all past events")
async def fetch_past_events():
    """
    Retrieves the list of all events and their information
    """
    # TODO fetch only group
    return await crud.fetch_all(events, exclusions={"end_ts": None})


@router.put("/{event_id}/", response_model=EventOut, summary="Update information about a specific event")
async def update_event(
    payload: EventIn,
    event_id: int = Path(..., gt=0),
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.device])
):
    """
    Based on a event_id, updates information about the specified event
    """
    return await crud.update_entry(events, payload, event_id)


@router.delete("/{event_id}/", response_model=EventOut, summary="Delete a specific event")
async def delete_event(event_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Based on a event_id, deletes the specified event
    """
    return await crud.delete_entry(events, event_id)
