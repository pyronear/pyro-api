from datetime import datetime
from typing import Any, Dict, List, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings


def _push_subscription_response(entry: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": entry["id"],
        "endpoint": entry["endpoint"],
        "expiration_time": entry["expiration_time"],
        "user_agent": entry["user_agent"],
        "created_at": datetime.fromisoformat(entry["created_at"]).isoformat(),
        "updated_at": datetime.fromisoformat(entry["updated_at"]).isoformat(),
    }


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail"),
    [
        (None, 401, "Not authenticated"),
        (0, 503, "Push notifications are disabled"),
    ],
)
@pytest.mark.asyncio
async def test_get_public_key_disabled(
    async_client: AsyncClient,
    user_session: AsyncSession,
    user_idx: Union[int, None],
    status_code: int,
    status_detail: str,
    monkeypatch,
):
    monkeypatch.setattr(settings, "VAPID_PUBLIC_KEY", None)
    monkeypatch.setattr(settings, "VAPID_PRIVATE_KEY", None)
    monkeypatch.setattr(settings, "VAPID_SUBJECT", None)

    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get("/push-subscriptions/public-key", headers=auth)
    assert response.status_code == status_code
    assert response.json()["detail"] == status_detail


@pytest.mark.asyncio
async def test_get_public_key_enabled(
    async_client: AsyncClient,
    user_session: AsyncSession,
    monkeypatch,
):
    monkeypatch.setattr(settings, "VAPID_PUBLIC_KEY", "public-key")
    monkeypatch.setattr(settings, "VAPID_PRIVATE_KEY", "private-key")
    monkeypatch.setattr(settings, "VAPID_SUBJECT", "mailto:test@example.com")

    auth = pytest.get_token(
        pytest.user_table[0]["id"],
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )
    response = await async_client.get("/push-subscriptions/public-key", headers=auth)
    assert response.status_code == 200
    assert response.json() == {"public_key": "public-key"}


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code"),
    [
        (
            None,
            {
                "endpoint": "https://push.example.com/new-subscription",
                "keys": {"auth": "new-auth-key", "p256dh": "new-p256dh-key"},
                "user_agent": "iPhone Safari",
            },
            401,
        ),
        (
            0,
            {
                "endpoint": "https://push.example.com/new-subscription",
                "keys": {"auth": "new-auth-key", "p256dh": "new-p256dh-key"},
                "user_agent": "iPhone Safari",
            },
            200,
        ),
        (
            0,
            {
                "endpoint": pytest.push_subscription_table[0]["endpoint"],
                "keys": {"auth": "updated-auth-key", "p256dh": "updated-p256dh-key"},
                "user_agent": "Updated Agent",
            },
            200,
        ),
    ],
)
@pytest.mark.asyncio
async def test_register_push_subscription(
    async_client: AsyncClient,
    user_session: AsyncSession,
    user_idx: Union[int, None],
    payload: Dict[str, Any],
    status_code: int,
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.post("/push-subscriptions", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if response.status_code == 200:
        assert response.json()["endpoint"] == payload["endpoint"]
        assert response.json()["user_agent"] == payload["user_agent"]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_response"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, [_push_subscription_response(pytest.push_subscription_table[0])]),
        (1, 200, None, [_push_subscription_response(pytest.push_subscription_table[1])]),
        (2, 200, None, []),
    ],
)
@pytest.mark.asyncio
async def test_fetch_push_subscriptions(
    async_client: AsyncClient,
    push_subscription_session: AsyncSession,
    user_idx: Union[int, None],
    status_code: int,
    status_detail: Union[str, None],
    expected_response: Union[List[Dict[str, Any]], None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get("/push-subscriptions", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code == 200:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    ("user_idx", "subscription_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 1, 200, None),
        (0, 2, 403, "Access forbidden."),
        (1, 2, 200, None),
        (2, 1, 403, "Access forbidden."),
    ],
)
@pytest.mark.asyncio
async def test_delete_push_subscription(
    async_client: AsyncClient,
    push_subscription_session: AsyncSession,
    user_idx: Union[int, None],
    subscription_id: int,
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.delete(f"/push-subscriptions/{subscription_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code == 200:
        assert response.json() is None
