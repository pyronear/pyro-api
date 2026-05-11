# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import List, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Security, status

from app.api.dependencies import get_jwt, get_push_subscription_crud
from app.crud.crud_push_subscription import PushSubscriptionCRUD
from app.models import PushSubscription, UserRole
from app.schemas.login import TokenPayload
from app.schemas.push_subscriptions import (
    PushSubscriptionCreate,
    PushSubscriptionRead,
    PushSubscriptionUpsert,
    PushSubscriptionVapidPublicKey,
)
from app.services.push_notifications import push_notification_client
from app.services.telemetry import telemetry_client

router = APIRouter()


@router.get("/public-key", status_code=status.HTTP_200_OK, summary="Fetch the VAPID public key")
async def get_public_key(
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> PushSubscriptionVapidPublicKey:
    telemetry_client.capture(token_payload.sub, event="push-subscriptions-public-key")
    if not push_notification_client.is_enabled:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Push notifications are disabled")
    return PushSubscriptionVapidPublicKey(public_key=push_notification_client.get_public_key())


@router.post("/", status_code=status.HTTP_200_OK, summary="Register or update a push subscription")
async def register_push_subscription(
    payload: PushSubscriptionUpsert,
    subscriptions: PushSubscriptionCRUD = Depends(get_push_subscription_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> PushSubscriptionRead:
    telemetry_client.capture(token_payload.sub, event="push-subscriptions-upsert")
    subscription = await subscriptions.upsert_for_user(
        token_payload.sub,
        token_payload.organization_id,
        PushSubscriptionCreate(
            user_id=token_payload.sub,
            organization_id=token_payload.organization_id,
            endpoint=payload.endpoint,
            auth=payload.keys.auth,
            p256dh=payload.keys.p256dh,
            expiration_time=payload.expiration_time,
            user_agent=payload.user_agent,
        ),
    )
    return PushSubscriptionRead(**subscription.model_dump())


@router.get("/", status_code=status.HTTP_200_OK, summary="Fetch current user's push subscriptions")
async def fetch_push_subscriptions(
    subscriptions: PushSubscriptionCRUD = Depends(get_push_subscription_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> List[PushSubscriptionRead]:
    telemetry_client.capture(token_payload.sub, event="push-subscriptions-fetch")
    return [
        PushSubscriptionRead(**elt.model_dump())
        for elt in await subscriptions.fetch_all(filters=[("user_id", token_payload.sub)], order_by="created_at")
    ]


@router.delete("/{subscription_id}", status_code=status.HTTP_200_OK, summary="Delete a push subscription")
async def delete_push_subscription(
    subscription_id: int = Path(..., gt=0),
    subscriptions: PushSubscriptionCRUD = Depends(get_push_subscription_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> None:
    telemetry_client.capture(
        token_payload.sub,
        event="push-subscriptions-delete",
        properties={"subscription_id": subscription_id},
    )
    subscription = cast(PushSubscription, await subscriptions.get(subscription_id, strict=True))
    if subscription.user_id != token_payload.sub:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    await subscriptions.delete(subscription_id)
