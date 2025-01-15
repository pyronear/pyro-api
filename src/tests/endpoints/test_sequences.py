from typing import Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail"),
    [
        (None, 401, "Not authenticated"),
        (0, 200, None),
        (1, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_fetch_sequences(
    async_client: AsyncClient,
    sequence_session: AsyncSession,
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

    response = await async_client.get("/sequences/", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.sequence_table


@pytest.mark.parametrize(
    ("user_idx", "sequence_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 1, 200, None),
        (0, 2, 404, "Table sequences has no corresponding entry."),
        (1, 1, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_delete_sequence(
    async_client: AsyncClient,
    sequence_session: AsyncSession,
    user_idx: Union[int, None],
    sequence_id: int,
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

    response = await async_client.delete(f"/sequences/{sequence_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None
