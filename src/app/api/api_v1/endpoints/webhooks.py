# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Annotated, cast

from fastapi import APIRouter, Depends, Path, Security, status

from app.api.dependencies import get_jwt, get_webhook_crud
from app.crud import WebhookCRUD
from app.models import UserRole, Webhook
from app.schemas.login import TokenPayload
from app.schemas.webhooks import WebhookCreate, WebhookCreation
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new webhook")
async def register_webhook(
    payload: WebhookCreate,
    webhooks: Annotated[WebhookCRUD, Depends(get_webhook_crud)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> Webhook:
    telemetry_client.capture(token_payload.sub, event="webhooks-create")
    return await webhooks.create(WebhookCreation(url=str(payload.url)))


@router.get("/{webhook_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific webhook")
async def get_webhook(
    webhook_id: Annotated[int, Path(gt=0)],
    webhooks: Annotated[WebhookCRUD, Depends(get_webhook_crud)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> Webhook:
    telemetry_client.capture(token_payload.sub, event="webhooks-get", properties={"webhook_id": webhook_id})
    return cast(Webhook, await webhooks.get(webhook_id, strict=True))


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the webhooks")
async def fetch_webhooks(
    webhooks: Annotated[WebhookCRUD, Depends(get_webhook_crud)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> list[Webhook]:
    telemetry_client.capture(token_payload.sub, event="webhooks-fetch")
    return [elt for elt in await webhooks.fetch_all()]


@router.delete("/{webhook_id}", status_code=status.HTTP_200_OK, summary="Delete a webhook")
async def delete_webhook(
    webhook_id: Annotated[int, Path(gt=0)],
    webhooks: Annotated[WebhookCRUD, Depends(get_webhook_crud)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> None:
    telemetry_client.capture(token_payload.sub, event="webhooks-deletion", properties={"webhook_id": webhook_id})
    await webhooks.delete(webhook_id)
