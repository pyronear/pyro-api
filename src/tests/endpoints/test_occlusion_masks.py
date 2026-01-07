from typing import Any, Dict, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (None, {"pose_id": 1, "mask": "(0.1,0.1,0.9,0.9)"}, 401, "Not authenticated"),
        (2, {"pose_id": 1, "mask": "(0.1,0.1,0.9,0.9)"}, 403, "Incompatible token scope."),
        (0, {"pose_id": 0, "mask": "(0.1,0.1,0.9,0.9)"}, 422, None),
        (0, {"pose_id": 999, "mask": "(0.1,0.1,0.9,0.9)"}, 404, "Table Pose has no corresponding entry."),
        (1, {"pose_id": 3, "mask": "(0.1,0.1,0.9,0.9)"}, 403, "Access forbidden."),  # agent org 1, camera org 2
        (0, {"pose_id": 1, "mask": "invalid"}, 422, None),
        (0, {"pose_id": 1, "mask": "(0.1,0.1,0.9,0.9)"}, 201, None),
        (1, {"pose_id": 1, "mask": "(0.1,0.1,0.9,0.9)"}, 201, None),
    ],
)
@pytest.mark.asyncio
async def test_create_occlusion_mask(
    async_client: AsyncClient,
    pose_session: AsyncSession,
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

    response = await async_client.post("/occlusion_masks", json=payload, headers=auth)

    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail

    if response.status_code == 201:
        json_resp = response.json()
        assert "id" in json_resp
        assert json_resp["pose_id"] == payload["pose_id"]
        assert json_resp["mask"] == payload["mask"]
        assert "created_at" in json_resp


@pytest.mark.parametrize(
    ("user_idx", "mask_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (2, 1, 403, "Incompatible token scope."),
        (0, 0, 422, None),
        (0, 999, 404, "Table OcclusionMask has no corresponding entry."),
        (1, 4, 403, "Access forbidden."),  # agent wrong org
        (1, 1, 200, None),
        (0, 2, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_get_occlusion_mask(
    async_client: AsyncClient,
    occlusion_mask_session: AsyncSession,
    user_idx: Union[int, None],
    mask_id: int,
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

    response = await async_client.get(f"/occlusion_masks/{mask_id}", headers=auth)

    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail

    if response.status_code == 200:
        json_resp = response.json()
        assert json_resp["id"] == mask_id
        assert "pose_id" in json_resp
        assert "mask" in json_resp
        assert "created_at" in json_resp


@pytest.mark.parametrize(
    ("user_idx", "mask_id", "payload", "status_code", "status_detail"),
    [
        (None, 1, {"mask": "(0.2,0.2,0.8,0.8)"}, 401, "Not authenticated"),
        (2, 1, {"mask": "(0.2,0.2,0.8,0.8)"}, 403, "Incompatible token scope."),
        (0, 0, {"mask": "(0.2,0.2,0.8,0.8)"}, 422, None),
        (0, 999, {"mask": "(0.2,0.2,0.8,0.8)"}, 404, "Table OcclusionMask has no corresponding entry."),
        (1, 4, {"mask": "(0.2,0.2,0.8,0.8)"}, 403, "Access forbidden."),  # agent org mismatch
        (0, 1, {"mask": "bad_format"}, 422, None),
        (0, 1, {"mask": "(0.2,0.2,0.8,0.8)"}, 200, None),
        (1, 1, {"mask": "(0.3,0.3,0.7,0.7)"}, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_update_occlusion_mask(
    async_client: AsyncClient,
    occlusion_mask_session: AsyncSession,
    user_idx: Union[int, None],
    mask_id: int,
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

    response = await async_client.patch(f"/occlusion_masks/{mask_id}", json=payload, headers=auth)

    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail

    if response.status_code == 200:
        json_resp = response.json()
        assert json_resp["id"] == mask_id
        assert json_resp["mask"] == payload["mask"]


@pytest.mark.parametrize(
    ("user_idx", "mask_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (2, 1, 403, "Incompatible token scope."),
        (0, 0, 422, None),
        (0, 999, 404, "Table OcclusionMask has no corresponding entry."),
        (1, 4, 403, "Access forbidden."),  # agent wrong org
        (1, 1, 200, None),
        (0, 2, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_delete_occlusion_mask(
    async_client: AsyncClient,
    occlusion_mask_session: AsyncSession,
    user_idx: Union[int, None],
    mask_id: int,
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

    response = await async_client.delete(f"/occlusion_masks/{mask_id}", headers=auth)

    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
