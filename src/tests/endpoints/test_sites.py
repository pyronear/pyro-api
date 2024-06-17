from typing import Any, Dict, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            {"name": "pyro-site", "type": "SDIS"},
            401,
            "Not authenticated",
        ),
        (0, {"name": "pyro-site", "type": "SDIS"}, 422, None),
        (
            0,
            {"name": "pyro-site", "type": "SDIS"},
            201,
            None,
        ),
        (
            1,
            {"name": "pyro-site", "type": "SDIS"},
            201,
            None,
        ),
        (
            2,
            {"name": "pyro-site", "type": "SDIS"},
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio()
async def test_create_site(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    user_idx: Union[int, None],
    payload: Dict[str, Any],
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(pytest.user_table[user_idx]["id"], pytest.user_table[user_idx]["role"].split())

    response = await async_client.post("/site", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert {
            k: v for k, v in response.json().items() if k not in {"id", "created_at", "last_active_at", "is_trustable"}
        } == payload
