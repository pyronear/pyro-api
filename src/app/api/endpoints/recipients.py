# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from fastapi import APIRouter, Path, Security, status

from app.api import crud
from app.api.deps import get_current_access
from app.db import recipients
from app.models import AccessType
from app.schemas import RecipientIn, RecipientOut

router = APIRouter(dependencies=[Security(get_current_access, scopes=[AccessType.admin])])


@router.post("/", response_model=RecipientOut, status_code=status.HTTP_201_CREATED, summary="Create a new recipient")
async def create_recipient(
    payload: RecipientIn,
):
    """
    Creates a new recipient based on the given information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(recipients, payload)


@router.get("/{recipient_id}/", response_model=RecipientOut, summary="Get information about a specific recipient")
async def get_recipient(recipient_id: int = Path(..., gt=0)):
    """
    Retrieve information about the recipient with the given recipient_id
    """
    return await crud.get_entry(recipients, recipient_id)


@router.get("/", response_model=List[RecipientOut], summary="Get the list of all recipients")
async def fetch_recipients():
    """
    Retrieves the list of all recipients and their information
    """
    return await crud.fetch_all(recipients)


@router.get(
    "/group-recipients/{group_id}/",
    response_model=List[RecipientOut],
    summary="Get the list of all recipients for the given group",
)
async def fetch_recipients_for_group(group_id: int = Path(..., gt=0)):
    """
    Retrieves the list of all recipients for the given group and their information
    """
    return await crud.fetch_all(recipients, {"group_id": group_id})


@router.put("/{recipient_id}/", response_model=RecipientOut, summary="Update information about a specific recipient")
async def update_recipient(payload: RecipientIn, recipient_id: int = Path(..., gt=0)):
    """
    Given its ID, updates information about the specified recipient
    """
    return await crud.update_entry(recipients, payload, recipient_id)


@router.delete("/{recipient_id}/", response_model=RecipientOut, summary="Delete a specific recipient")
async def delete_recipient(recipient_id: int = Path(..., gt=0)):
    """
    Based on a recipient_id, deletes the specified recipient
    """
    return await crud.delete_entry(recipients, recipient_id)
