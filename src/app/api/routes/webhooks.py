# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from fastapi import APIRouter, Path, Security, status

from app.api import crud
from app.api.deps import get_current_access
from app.api.schemas import WebhookIn, WebhookOut
from app.db import webhooks

router = APIRouter()


@router.post("/", response_model=WebhookOut, status_code=status.HTTP_201_CREATED, summary="Create a new webhook")
async def create_webhook(payload: WebhookIn, _=Security(get_current_access, scopes=["admin"])):
    """
    Creates a new webhook with the specified information

    Below, click on "Schema" for more detailed information about arguments
    or "Example Value" to get a concrete idea of arguments
    """
    return await crud.create_entry(webhooks, payload)


@router.get("/{webhook_id}/", response_model=WebhookOut, summary="Get information about a specific webhook")
async def get_webhook(webhook_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=["admin"])):
    """
    Given its ID, retrieves information about the specified webhook
    """
    return await crud.get_entry(webhooks, webhook_id)


@router.get("/", response_model=List[WebhookOut], summary="Get the list of all webhooks")
async def fetch_webhooks(_=Security(get_current_access, scopes=["admin"])):
    """
    Retrieves the list of all webhooks and their information
    """
    return await crud.fetch_all(webhooks)


@router.put("/{webhook_id}/", response_model=WebhookOut, summary="Update information about a specific webhook")
async def update_webhook(
    payload: WebhookIn, webhook_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=["admin"])
):
    """
    Given its ID, updates information about the specified webhook
    """
    return await crud.update_entry(webhooks, payload, webhook_id)


@router.delete("/{webhook_id}/", response_model=WebhookOut, summary="Delete a specific webhook")
async def delete_webhook(webhook_id: int = Path(..., gt=0), _=Security(get_current_access, scopes=["admin"])):
    """
    Given its ID, deletes a specific webhook
    """
    return await crud.delete_entry(webhooks, webhook_id)
