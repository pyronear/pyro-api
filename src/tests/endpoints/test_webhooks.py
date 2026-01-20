from typing import Any

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            {"url": "http://www.google.com/"},
            401,
            "Not authenticated",
        ),
        (
            0,
            {"url": pytest.webhook_table[0]["url"]},
            409,
            None,
        ),
        (
            0,
            {"url": "http://www.google.com/"},
            201,
            None,
        ),
        (
            1,
            {"url": "http://www.google.com/"},
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            {"url": "http://www.google.com/"},
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_webhook(
    async_client: AsyncClient,
    webhook_session: AsyncSession,
    user_idx: int | None,
    payload: dict[str, Any],
    status_code: int,
    status_detail: str | None,
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.post("/webhooks", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert {k: v for k, v in response.json().items() if k != "id"} == payload


@pytest.mark.parametrize(
    ("user_idx", "webhook_id", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 1, 200, None, 0),
        (1, 1, 403, "Incompatible token scope.", 0),
        (2, 1, 403, "Incompatible token scope.", 0),
    ],
)
@pytest.mark.asyncio
async def test_get_webhook(
    async_client: AsyncClient,
    webhook_session: AsyncSession,
    user_idx: int | None,
    webhook_id: int,
    status_code: int,
    status_detail: str | None,
    expected_idx: int | None,
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.get(f"/webhooks/{webhook_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.webhook_table[expected_idx]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_response"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, pytest.webhook_table),
        (1, 403, "Incompatible token scope.", None),
        (2, 403, "Incompatible token scope.", None),
    ],
)
@pytest.mark.asyncio
async def test_fetch_webhooks(
    async_client: AsyncClient,
    webhook_session: AsyncSession,
    user_idx: int | None,
    status_code: int,
    status_detail: str | None,
    expected_response: list[dict[str, Any]] | None,
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get("/webhooks", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    ("user_idx", "webhook_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 1, 200, None),
        (1, 1, 403, "Incompatible token scope."),
        (1, 2, 403, "Incompatible token scope."),
        (2, 2, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_delete_webhook(
    async_client: AsyncClient,
    webhook_session: AsyncSession,
    user_idx: int | None,
    webhook_id: int,
    status_code: int,
    status_detail: str | None,
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.delete(f"/webhooks/{webhook_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None
