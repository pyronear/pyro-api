# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.time import utcnow
from app.crud.base import BaseCRUD
from app.models import PushSubscription
from app.schemas.push_subscriptions import PushSubscriptionCreate, PushSubscriptionUpdate

__all__ = ["PushSubscriptionCRUD"]


class PushSubscriptionCRUD(BaseCRUD[PushSubscription, PushSubscriptionCreate, PushSubscriptionUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        """Initialize push subscription CRUD."""
        super().__init__(session, PushSubscription)

    async def upsert_for_user(
        self,
        user_id: int,
        organization_id: int,
        payload: PushSubscriptionCreate,
    ) -> PushSubscription:
        existing = await self.get_by("endpoint", payload.endpoint, strict=False)
        if existing is None:
            return await self.create(
                PushSubscriptionCreate(
                    user_id=user_id,
                    organization_id=organization_id,
                    endpoint=payload.endpoint,
                    auth=payload.auth,
                    p256dh=payload.p256dh,
                    expiration_time=payload.expiration_time,
                    user_agent=payload.user_agent,
                )
            )

        return await self.update(
            existing.id,
            PushSubscriptionUpdate(
                user_id=user_id,
                organization_id=organization_id,
                endpoint=payload.endpoint,
                auth=payload.auth,
                p256dh=payload.p256dh,
                expiration_time=payload.expiration_time,
                user_agent=payload.user_agent,
                updated_at=utcnow(),
            ),
        )
