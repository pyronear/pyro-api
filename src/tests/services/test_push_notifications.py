import json
from datetime import datetime

import pytest

from app.core.config import settings
from app.models import PushSubscription
from app.services.push_notifications import PushNotificationClient


def _subscription() -> PushSubscription:
    return PushSubscription(
        id=1,
        user_id=1,
        organization_id=1,
        endpoint="https://push.example.com/subscription",
        auth="auth-key",
        p256dh="p256dh-key",
    )


def test_push_notifications_disabled(monkeypatch):
    client = PushNotificationClient()
    monkeypatch.setattr(settings, "VAPID_PRIVATE_KEY", None)
    monkeypatch.setattr(settings, "VAPID_PUBLIC_KEY", None)
    monkeypatch.setattr(settings, "VAPID_SUBJECT", None)

    assert client.is_enabled is False
    with pytest.raises(AssertionError, match="Push notifications are not enabled"):
        client.ensure_enabled()

    client.notify_many(
        [_subscription()],
        alert_id=12,
        camera_name="Camera 1",
        created_at=datetime(2026, 4, 30, 12, 0, 0),
        sequence_azimuth=123.4,
    )


def test_push_notifications_send_payload(monkeypatch):
    client = PushNotificationClient()
    calls = []

    def fake_webpush(**kwargs):
        calls.append(kwargs)

    monkeypatch.setattr(settings, "PLATFORM_URL", "https://platform.example.com/")
    monkeypatch.setattr(settings, "VAPID_PRIVATE_KEY", "private-key")
    monkeypatch.setattr(settings, "VAPID_PUBLIC_KEY", "public-key")
    monkeypatch.setattr(settings, "VAPID_SUBJECT", "mailto:test@example.com")
    monkeypatch.setattr(settings, "PUSH_NOTIFICATIONS_TTL_SECONDS", 42)
    monkeypatch.setattr("pywebpush.webpush", fake_webpush)

    created_at = datetime(2026, 4, 30, 12, 0, 0)
    client.notify_many(
        [_subscription()],
        alert_id=12,
        camera_name="Camera 1",
        created_at=created_at,
        sequence_azimuth=123.4,
    )

    assert client.get_public_key() == "public-key"
    assert len(calls) == 1
    assert calls[0]["subscription_info"] == {
        "endpoint": "https://push.example.com/subscription",
        "keys": {"auth": "auth-key", "p256dh": "p256dh-key"},
    }
    assert calls[0]["vapid_private_key"] == "private-key"
    assert calls[0]["vapid_claims"] == {"sub": "mailto:test@example.com"}
    assert calls[0]["ttl"] == 42

    payload = json.loads(calls[0]["data"])
    assert payload == {
        "title": "Wildfire alert detected",
        "body": "Camera 1 at 2026-04-30T12:00:00 | Azimuth: 123.4 degrees",
        "tag": "alert-12",
        "url": "https://platform.example.com/alert/12",
        "data": {"alert_id": 12, "url": "https://platform.example.com/alert/12"},
    }


def test_push_notifications_logs_delivery_errors(monkeypatch, caplog):
    from pywebpush import WebPushException

    client = PushNotificationClient()

    def failing_webpush(**kwargs):
        raise WebPushException("delivery failed")

    monkeypatch.setattr(settings, "VAPID_PRIVATE_KEY", "private-key")
    monkeypatch.setattr(settings, "VAPID_PUBLIC_KEY", "public-key")
    monkeypatch.setattr(settings, "VAPID_SUBJECT", "mailto:test@example.com")
    monkeypatch.setattr("pywebpush.webpush", failing_webpush)

    client.notify_many(
        [_subscription()],
        alert_id=12,
        camera_name="Camera 1",
        created_at=datetime(2026, 4, 30, 12, 0, 0),
        sequence_azimuth=None,
    )

    assert "Failed to send web push notification to subscription 1" in caplog.text
