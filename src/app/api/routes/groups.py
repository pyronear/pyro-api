# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List

from fastapi import APIRouter, Path, Security, status

from app.api import crud
from app.api.deps import get_current_access
from app.api.schemas import AccessType, GroupIn, GroupOut
from app.db import groups

router = APIRouter()


@router.post("/", response_model=GroupOut, status_code=status.HTTP_201_CREATED, summary="Create a new group")
async def create_group(payload: GroupIn, _=Security(get_current_access, scopes=[AccessType.admin])):
    """Creates a new group based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(groups, payload)


@router.get("/{group_id}/", response_model=GroupOut, summary="Get information about a specific group")
async def get_group(group_id: int = Path(..., gt=0)):
    """
    Based on a group_id, retrieves information about the specified group
    """
    return await crud.get_entry(groups, group_id)


@router.get("/", response_model=List[GroupOut], summary="Get the list of all groups")
async def fetch_groups():
    """
    Retrieves the list of all groups and their information
    """
    return await crud.fetch_all(groups)


@router.put("/{group_id}/", response_model=GroupOut, summary="Update information about a specific group")
async def update_group(
    payload: GroupIn,
    group_id: int = Path(..., gt=0),
    _=Security(get_current_access, scopes=[AccessType.admin])
):
    """
    Based on a group_id, updates information about the specified group
    """
    return await crud.update_entry(groups, payload, group_id)


@router.delete("/{group_id}/", response_model=GroupOut, summary="Delete a specific group")
async def delete_group(group_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=[AccessType.admin])):
    """
    Based on a group_id, deletes the specified group
    """
    return await crud.delete_entry(groups, group_id)
