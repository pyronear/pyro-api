from typing import Any, Dict, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            {"login": "pyro_user", "password": "bar", "role": "user", "organization_id": 1},
            401,
            "Not authenticated",
        ),
        (
            1,
            {"login": "pyro_user", "password": "bar", "role": "user", "organization_id": 1},
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            {"login": "pyro_user", "password": "bar", "role": "user", "organization_id": 2},
            403,
            "Incompatible token scope.",
        ),
        (
            0,
            {"login": "first_login", "password": "bar", "role": "user", "organization_id": 1},
            409,
            "Login already taken",
        ),
        (
            0,
            {"login": "pyro_user", "organization_id": 1},
            422,
            None,
        ),
    ],
)
@pytest.mark.asyncio()
async def test_create_user(
    async_client: AsyncClient,
    user_session: AsyncSession,
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

    response = await async_client.post("/users", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert {k: v for k, v in response.json().items() if k != "created_at"} == {
            "login": payload["login"],
            "hashed_password": f"hashed_{payload['password']}",
            "role": payload["role"],
            "id": max(entry["id"] for entry in pytest.user_table) + 1,
        }


@pytest.mark.parametrize(
    ("user_idx", "user_id", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 0, 422, None, None),
        (0, 400, 404, "Table User has no corresponding entry.", None),
        (1, 1, 403, "Incompatible token scope.", None),
        (0, 1, 200, None, 0),
        (0, 2, 200, None, 1),
    ],
)
@pytest.mark.asyncio()
async def test_get_user(
    async_client: AsyncClient,
    user_session: AsyncSession,
    user_idx: Union[int, None],
    user_id: int,
    status_code: int,
    status_detail: Union[str, None],
    expected_idx: Union[int, None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get(f"/users/{user_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.user_table[expected_idx]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail"),
    [
        (None, 401, "Not authenticated"),
        (0, 200, None),
        (1, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio()
async def test_fetch_users(
    async_client: AsyncClient,
    user_session: AsyncSession,
    user_idx: Union[int, None],
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

    response = await async_client.get("/users/", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.user_table


@pytest.mark.parametrize(
    ("user_idx", "user_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 1, 200, None),
        (0, 2, 200, None),
        (1, 1, 403, "Incompatible token scope."),
        (1, 2, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio()
async def test_delete_user(
    async_client: AsyncClient,
    user_session: AsyncSession,
    user_idx: Union[int, None],
    user_id: int,
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

    response = await async_client.delete(f"/users/{user_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None


@pytest.mark.parametrize(
    ("user_idx", "user_id", "payload", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, {"password": "HeyPyro!"}, 401, "Not authenticated", None),
        (0, 1, {"login": "HeyPyro!"}, 422, None, None),
        (0, 1, {"password": "HeyPyro!"}, 200, None, 0),
        (0, 2, {"password": "HeyPyro!"}, 200, None, 1),
        (1, 1, {"password": "HeyPyro!"}, 403, "Incompatible token scope.", None),
        (1, 2, {"password": "HeyPyro!"}, 403, "Incompatible token scope.", None),
    ],
)
@pytest.mark.asyncio()
async def test_update_user_password(
    async_client: AsyncClient,
    user_session: AsyncSession,
    user_idx: Union[int, None],
    user_id: int,
    payload: Dict[str, Any],
    status_code: int,
    status_detail: Union[str, None],
    expected_idx: Union[int, None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.patch(f"/users/{user_id}", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == {
            "id": pytest.user_table[expected_idx]["id"],
            "created_at": pytest.user_table[expected_idx]["created_at"],
            "login": pytest.user_table[expected_idx]["login"],
            "hashed_password": f"hashed_{payload['password']}",
            "role": pytest.user_table[expected_idx]["role"],
            "organization_id": pytest.user_table[expected_idx]["organization_id"],
        }
