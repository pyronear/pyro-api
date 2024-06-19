from typing import Any, Dict, List, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            {"name": "pyro-site", "type": "sdis"},
            401,
            "Not authenticated",
        ),
        (
            0,
            {"name": "pyro-site", "type": "sdis"},
            201,
            None,
        ),
        (
            1,
            {"name": "pyro-site2", "type": "sdis"},
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            {"name": "pyro-site", "type": "sdis"},
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio()
async def test_create_site(
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
            pytest.user_table[user_idx]["site_id"],
        )

    response = await async_client.post("/sites", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert {
            k: v for k, v in response.json().items() if k not in {"id", "created_at", "last_active_at", "is_trustable"}
        } == payload


@pytest.mark.parametrize(
    ("user_idx", "site_id", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 1, 200, None, 0),
        (1, 1, 200, None, 0),
        (2, 1, 403, "Access forbidden.", 0),
    ],
)
@pytest.mark.asyncio()
async def test_get_site(
    async_client: AsyncClient,
    site_session: AsyncSession,
    user_idx: Union[int, None],
    site_id: int,
    status_code: int,
    status_detail: Union[str, None],
    expected_idx: Union[int, None],
):
    auth = None
    site_id_from_table = pytest.user_table[user_idx]["site_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            site_id_from_table,
        )

    response = await async_client.get(f"/sites/{site_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.site_table[expected_idx]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_response"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, pytest.site_table[0]),
        (1, 200, None, pytest.site_table[0]),
        (2, 200, None, pytest.site_table[1]),
    ],
)
@pytest.mark.asyncio()
async def test_fetch_sites(
    async_client: AsyncClient,
    site_session: AsyncSession,
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
            pytest.user_table[user_idx]["site_id"],
        )

    response = await async_client.get("/sites", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json()[0] == expected_response


@pytest.mark.parametrize(
    ("user_idx", "site_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 1, 200, None),
        (1, 1, 403, "Incompatible token scope."),
        (1, 2, 403, "Incompatible token scope."),
        (2, 2, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio()
async def test_delete_site(
    async_client: AsyncClient,
    site_session: AsyncSession,
    user_idx: Union[int, None],
    site_id: int,
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    site_id_from_table = pytest.user_table[user_idx]["site_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            site_id_from_table,
        )

    response = await async_client.delete(f"/sites/{site_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None
