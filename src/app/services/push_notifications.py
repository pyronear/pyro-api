# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import json
import logging
from datetime import datetime

from app.core.config import settings
from app.models import PushSubscription

logger = logging.getLogger("uvicorn.error")

__all__ = ["push_notification_client"]


class PushNotificationClient:
    @property
    def is_enabled(self) -> bool:
        return all([settings.VAPID_PRIVATE_KEY, settings.VAPID_PUBLIC_KEY, settings.VAPID_SUBJECT])

    def ensure_enabled(self) -> None:
        if not self.is_enabled:
            raise AssertionError("Push notifications are not enabled")

    def get_public_key(self) -> str:
        self.ensure_enabled()
        return settings.VAPID_PUBLIC_KEY or ""

    def notify_many(
        self,
        subscriptions: list[PushSubscription],
        *,
        alert_id: int,
        camera_name: str,
        created_at: datetime,
        sequence_azimuth: float | None,
    ) -> None:
        if not self.is_enabled:
            logger.info("Push notifications are disabled, skipping delivery")
            return

        from pywebpush import WebPushException, webpush  # type: ignore[import-untyped]

        alert_url = self._build_alert_url(alert_id)
        payload = json.dumps({
            "title": "Wildfire alert detected",
            "body": self._build_body(camera_name, created_at, sequence_azimuth),
            "tag": f"alert-{alert_id}",
            "url": alert_url,
            "data": {"alert_id": alert_id, "url": alert_url},
        })

        for subscription in subscriptions:
            try:
                webpush(
                    subscription_info={
                        "endpoint": subscription.endpoint,
                        "keys": {"auth": subscription.auth, "p256dh": subscription.p256dh},
                    },
                    data=payload,
                    vapid_private_key=settings.VAPID_PRIVATE_KEY,
                    vapid_claims={"sub": settings.VAPID_SUBJECT},
                    ttl=settings.PUSH_NOTIFICATIONS_TTL_SECONDS,
                )
            except WebPushException as error:
                logger.error("Failed to send web push notification to subscription %s: %s", subscription.id, error)

    def _build_alert_url(self, alert_id: int) -> str:
        base_url = settings.PLATFORM_URL.rstrip("/")
        return f"{base_url}/alert/{alert_id}"

    def _build_body(self, camera_name: str, created_at: datetime, sequence_azimuth: float | None) -> str:
        body = f"{camera_name} at {created_at.isoformat()}"
        if sequence_azimuth is not None:
            body += f" | Azimuth: {sequence_azimuth:.1f} degrees"
        return body


push_notification_client = PushNotificationClient()
