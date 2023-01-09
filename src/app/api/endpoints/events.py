# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List, cast

from fastapi import APIRouter, Depends, Path, Security, status
from sqlalchemy import and_

from app.api import crud
from app.api.crud.authorizations import check_group_read, check_group_update, is_admin_access
from app.api.crud.groups import get_entity_group_id
from app.api.deps import get_current_access, get_db
from app.db import events
from app.models import Access, AccessType, Alert, Device, Event
from app.schemas import Acknowledgement, AcknowledgementOut, EventIn, EventOut, EventUpdate

router = APIRouter()


@router.post("/", response_model=EventOut, status_code=status.HTTP_201_CREATED, summary="Create a new event")
async def create_event(payload: EventIn, _=Security(get_current_access, scopes=[AccessType.admin, AccessType.device])):
    """Creates a new event based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(events, payload)


@router.get("/{event_id}/", response_model=EventOut, summary="Get information about a specific event")
async def get_event(
    event_id: int = Path(..., gt=0), requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """
    Based on a event_id, retrieves information about the specified event
    """
    requested_group_id = await get_entity_group_id(events, event_id)
    await check_group_read(requester.id, cast(int, requested_group_id))
    return await crud.get_entry(events, event_id)


@router.get("/", response_model=List[EventOut], summary="Get the list of all events")
async def fetch_events(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of all events and their information
    """
    if await is_admin_access(requester.id):
        return await crud.fetch_all(events)
    else:
        retrieved_events = (
            session.query(Event).join(Alert).join(Device).join(Access).filter(Access.group_id == requester.group_id)
        )
        retrieved_events = [x.__dict__ for x in retrieved_events.all()]
        return retrieved_events


@router.get("/past", response_model=List[EventOut], summary="Get the list of all past events")
async def fetch_past_events(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of all events and their information
    """
    if await is_admin_access(requester.id):
        return await crud.fetch_all(events, exclusions={"end_ts": None})
    else:
        retrieved_events = (
            session.query(Event)
            .join(Alert)
            .join(Device)
            .join(Access)
            .filter(and_(Access.group_id == requester.group_id, Event.end_ts.isnot(None)))
        )
        retrieved_events = [x.__dict__ for x in retrieved_events.all()]
        return retrieved_events


@router.put("/{event_id}/", response_model=EventOut, summary="Update information about a specific event")
async def update_event(
    payload: EventUpdate,
    event_id: int = Path(..., gt=0),
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.device]),
):
    """
    Based on a event_id, updates information about the specified event
    """
    requested_group_id = await get_entity_group_id(events, event_id)
    await check_group_update(requester.id, cast(int, requested_group_id))
    return await crud.update_entry(events, payload, event_id)


@router.put("/{event_id}/acknowledge", response_model=AcknowledgementOut, summary="Acknowledge an existing event")
async def acknowledge_event(
    event_id: int = Path(..., gt=0), requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user])
):
    """
    Based on a event_id, acknowledge the specified event
    """
    requested_group_id = await get_entity_group_id(events, event_id)
    await check_group_update(requester.id, cast(int, requested_group_id))
    return await crud.update_entry(events, Acknowledgement(is_acknowledged=True), event_id)


@router.delete("/{event_id}/", response_model=EventOut, summary="Delete a specific event")
async def delete_event(
    event_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=[AccessType.admin]),
    session=Depends(get_db),
):
    """
    Based on a event_id, deletes the specified event
    """
    return await crud.delete_entry(events, event_id)


@router.get(
    "/unacknowledged", response_model=List[EventOut], summary="Get the list of events that haven't been acknowledged"
)
async def fetch_unacknowledged_events(
    requester=Security(get_current_access, scopes=[AccessType.admin, AccessType.user]), session=Depends(get_db)
):
    """
    Retrieves the list of non confirmed alerts and their information
    """
    if await is_admin_access(requester.id):
        return await crud.fetch_all(events, {"is_acknowledged": False})
    else:
        retrieved_events = (
            session.query(Event)
            .join(Alert)
            .join(Device)
            .join(Access)
            .filter(and_(Access.group_id == requester.group_id, Event.is_acknowledged.is_(False)))
        )
        retrieved_events = [x.__dict__ for x in retrieved_events.all()]
        return retrieved_events
