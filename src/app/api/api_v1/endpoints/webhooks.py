# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Annotated, cast

from fastapi import APIRouter, Depends, Path, Security, status
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.dependencies import get_jwt
from app.crud import WebhookCRUD
from app.db import get_session
from app.models import UserRole, Webhook
from app.schemas.login import TokenPayload
from app.schemas.webhooks import WebhookCreate, WebhookCreation
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.post("/", status_code=status.HTTP_201_CREATED, summary="Register a new webhook")
async def register_webhook(
    payload: WebhookCreate,
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> Webhook:
    telemetry_client.capture(token_payload.sub, event="webhooks-create")
    return await WebhookCRUD(session=session).create(WebhookCreation(url=str(payload.url)))


@router.get("/{webhook_id}", status_code=status.HTTP_200_OK, summary="Fetch the information of a specific webhook")
async def get_webhook(
    webhook_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> Webhook:
    telemetry_client.capture(token_payload.sub, event="webhooks-get", properties={"webhook_id": webhook_id})
    return cast(Webhook, await WebhookCRUD(session=session).get(webhook_id, strict=True))


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch all the webhooks")
async def fetch_webhooks(
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> list[Webhook]:
    telemetry_client.capture(token_payload.sub, event="webhooks-fetch")
    return [elt for elt in await WebhookCRUD(session=session).fetch_all()]


@router.delete("/{webhook_id}", status_code=status.HTTP_200_OK, summary="Delete a webhook")
async def delete_webhook(
    webhook_id: Annotated[int, Path(gt=0)],
    session: Annotated[AsyncSession, Depends(get_session)],
    token_payload: Annotated[TokenPayload, Security(get_jwt, scopes=[UserRole.ADMIN])],
) -> None:
    telemetry_client.capture(token_payload.sub, event="webhooks-deletion", properties={"webhook_id": webhook_id})
    await WebhookCRUD(session=session).delete(webhook_id)
