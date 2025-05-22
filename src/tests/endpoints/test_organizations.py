from typing import Any, Dict, List, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            {"name": "pyro-organization"},
            401,
            "Not authenticated",
        ),
        (
            0,
            {"name": "pyro-organization"},
            201,
            None,
        ),
        (
            1,
            {"name": "pyro-organization2"},
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            {"name": "pyro-organization"},
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_organization(
    async_client: AsyncClient,
    user_idx: Union[int, None],
    payload: Dict[str, Any],
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

    response = await async_client.post("/organizations", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert {k: v for k, v in response.json().items() if k not in {"id", "telegram_id", "slack_hook"}} == payload


@pytest.mark.parametrize(
    ("user_idx", "organization_id", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 1, 200, None, 0),
        (1, 1, 403, "Incompatible token scope.", 0),
        (2, 1, 403, "Incompatible token scope.", 0),
    ],
)
@pytest.mark.asyncio
async def test_get_organization(
    async_client: AsyncClient,
    organization_session: AsyncSession,
    user_idx: Union[int, None],
    organization_id: int,
    status_code: int,
    status_detail: Union[str, None],
    expected_idx: Union[int, None],
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.get(f"/organizations/{organization_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.organization_table[expected_idx]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_response"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, pytest.organization_table),
        (1, 403, "Incompatible token scope.", None),
        (2, 403, "Incompatible token scope.", None),
    ],
)
@pytest.mark.asyncio
async def test_fetch_organizations(
    async_client: AsyncClient,
    organization_session: AsyncSession,
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

    response = await async_client.get("/organizations", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    ("user_idx", "organization_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 1, 200, None),
        (1, 1, 403, "Incompatible token scope."),
        (1, 2, 403, "Incompatible token scope."),
        (2, 2, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_delete_organization(
    async_client: AsyncClient,
    organization_session: AsyncSession,
    user_idx: Union[int, None],
    organization_id: int,
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.delete(f"/organizations/{organization_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None


@pytest.mark.parametrize(
    ("user_idx", "organization_id", "payload", "status_code", "status_detail"),
    [
        (
            None,
            1,
            {"slack_hook": "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"},
            401,
            "Not authenticated",
        ),
        (0, 1, {"slack_hook": "test"}, 422, None),
        (0, 1, {"slack_hook": "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"}, 200, None),
        (
            1,
            2,
            {"slack_hook": "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"},
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            2,
            {"slack_hook": "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"},
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_slack_hook(
    async_client: AsyncClient,
    organization_session: AsyncSession,
    user_idx: Union[int, None],
    organization_id: int,
    payload: str,
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.patch(f"/organizations/slack-hook/{organization_id}", json=payload, headers=auth)

    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert str(response.json()["detail"]) == status_detail

    if response.status_code // 100 == 2:
        assert response.json()["slack_hook"] == "https://hooks.slack.com/services/TEST123/TEST123/testTEST123"
