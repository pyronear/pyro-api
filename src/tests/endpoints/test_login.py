from typing import Any

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("payload", "status_code", "status_detail"),
    [
        ({"username": "foo"}, 422, None),
        ({"username": "foo", "password": "bar"}, 401, None),
        ({"username": "first_login", "password": "pwd"}, 401, None),
        ({"username": "first_login", "password": "first_pwd"}, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_login_with_creds(
    async_client: AsyncClient,
    user_session: AsyncSession,
    payload: dict[str, Any],
    status_code: int,
    status_detail: str | None,
):
    response = await async_client.post("/login/creds", data=payload)
    assert response.status_code == status_code
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        response_json = response.json()
        assert response_json["token_type"] == "bearer"  # noqa: S105
        assert isinstance(response_json["access_token"], str)
        assert len(response_json["access_token"]) == 171
