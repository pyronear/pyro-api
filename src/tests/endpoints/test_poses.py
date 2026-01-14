from typing import Any, Dict, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            {"camera_id": 1, "azimuth": 45.0, "patrol_id": 1},
            401,
            "Not authenticated",
        ),
        (
            0,
            {"camera_id": 1, "patrol_id": 1},
            422,
            None,
        ),
        (
            0,
            {"camera_id": 999, "azimuth": 45.0, "patrol_id": 1},
            404,
            "Table Camera has no corresponding entry.",
        ),
        (
            2,  # org 2
            {"camera_id": 1, "azimuth": 45.0, "patrol_id": 1},  # camera 1 = org 1
            403,
            "Incompatible token scope.",
        ),
        (
            0,
            {"camera_id": 1, "azimuth": 45.0, "patrol_id": 1},
            201,
            None,
        ),
        (
            1,
            {"camera_id": 1, "azimuth": 90.0, "patrol_id": 120},
            201,
            None,
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_pose(
    async_client: AsyncClient,
    camera_session: AsyncSession,
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

    response = await async_client.post("/poses", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail

    if response.status_code == 201:
        json_resp = response.json()

        assert "id" in json_resp
        assert json_resp["camera_id"] == payload["camera_id"]
        assert json_resp["azimuth"] == payload["azimuth"]
        assert json_resp.get("patrol_id") == payload.get("patrol_id")


@pytest.mark.parametrize(
    ("cam_idx", "payload", "status_code", "status_detail"),
    [
        (
            0,
            {"camera_id": 1, "azimuth": 45.0, "patrol_id": 1},
            201,
            None,
        ),
        (
            0,
            {"camera_id": 2, "azimuth": 45.0, "patrol_id": 1},
            403,
            "Access forbidden.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_pose_camera_scope(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    cam_idx: int,
    payload: Dict[str, Any],
    status_code: int,
    status_detail: Union[str, None],
):
    auth = pytest.get_token(
        pytest.camera_table[cam_idx]["id"],
        ["camera"],
        pytest.camera_table[cam_idx]["organization_id"],
    )

    response = await async_client.post("/poses", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail

    if response.status_code == 201:
        json_resp = response.json()
        assert json_resp["camera_id"] == payload["camera_id"]
        assert json_resp["azimuth"] == payload["azimuth"]
        assert json_resp.get("patrol_id") == payload.get("patrol_id")


@pytest.mark.parametrize(
    ("user_idx", "pose_id", "status_code", "status_detail", "expected_pose"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 0, 422, None, None),
        (0, 999, 404, "Table Pose has no corresponding entry.", None),
        (2, 1, 403, "Access forbidden.", None),
        (
            0,
            1,
            200,
            None,
            {"id": 1, "camera_id": 1, "azimuth": 45.0, "patrol_id": 1},
        ),
        (
            1,
            2,
            200,
            None,
            {"id": 2, "camera_id": 1, "azimuth": 90.0, "patrol_id": 1},
        ),
    ],
)
@pytest.mark.asyncio
async def test_get_pose(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    pose_session: AsyncSession,
    user_idx: Union[int, None],
    pose_id: int,
    status_code: int,
    status_detail: Union[str, None],
    expected_pose: Union[dict, None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get(f"/poses/{pose_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail

    if response.status_code == 200:
        json_resp = response.json()
        assert json_resp == expected_pose


@pytest.mark.parametrize(
    ("user_idx", "pose_id", "payload", "status_code", "status_detail", "expected_updated"),
    [
        (None, 1, {"azimuth": 50.0}, 401, "Not authenticated", None),
        (0, 0, {"azimuth": 50.0}, 422, None, None),
        (0, 999, {"azimuth": 50.0}, 404, "Table Pose has no corresponding entry.", None),
        (2, 1, {"azimuth": 50.0}, 403, "Incompatible token scope.", None),
        (
            0,
            1,
            {"azimuth": 123.4, "patrol_id": 123},
            200,
            None,
            {"id": 1, "camera_id": 1, "azimuth": 123.4, "patrol_id": 123},
        ),
        (
            1,
            2,
            {"patrol_id": 456},
            200,
            None,
            {"id": 2, "camera_id": 1, "azimuth": 90.0, "patrol_id": 456},
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_pose(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    pose_session: AsyncSession,
    user_idx: Union[int, None],
    pose_id: int,
    payload: dict,
    status_code: int,
    status_detail: Union[str, None],
    expected_updated: Union[dict, None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.patch(f"/poses/{pose_id}", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail

    if response.status_code == 200:
        json_resp = response.json()
        assert json_resp == expected_updated


@pytest.mark.parametrize(
    ("cam_idx", "pose_id", "payload", "status_code", "status_detail"),
    [
        (0, 1, {"azimuth": 111.1}, 200, None),
        (0, 3, {"azimuth": 111.1}, 403, "Access forbidden."),
    ],
)
@pytest.mark.asyncio
async def test_update_pose_camera_scope(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    pose_session: AsyncSession,
    cam_idx: int,
    pose_id: int,
    payload: dict,
    status_code: int,
    status_detail: Union[str, None],
):
    auth = pytest.get_token(
        pytest.camera_table[cam_idx]["id"],
        ["camera"],
        pytest.camera_table[cam_idx]["organization_id"],
    )

    response = await async_client.patch(f"/poses/{pose_id}", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code == 200:
        json_resp = response.json()
        assert json_resp["id"] == pose_id
        assert json_resp["azimuth"] == payload["azimuth"]


@pytest.mark.parametrize(
    ("user_idx", "pose_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 0, 422, None),
        (1, 1, 403, "Incompatible token scope."),
        (2, 1, 403, "Incompatible token scope."),
        (0, 999, 404, "Table Pose has no corresponding entry."),
        (0, 1, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_delete_pose(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    pose_session: AsyncSession,
    user_idx: Union[int, None],
    pose_id: int,
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

    response = await async_client.delete(f"/poses/{pose_id}", headers=auth)

    assert response.status_code == status_code, print(response.__dict__)

    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail


@pytest.mark.parametrize(
    ("user_idx", "cam_idx", "pose_id", "status_code", "expected_count"),
    [
        (None, None, 1, 401, None),
        (0, None, 1, 200, 2),  # admin
        (1, None, 1, 200, 2),  # agent
        (2, None, 1, 403, 2),  # user from other org
        (None, 0, 1, 200, 2),  # cam
        (None, 1, 1, 403, 2),  # cam from other org
    ],
)
@pytest.mark.asyncio
async def test_list_pose_occlusion_masks(
    async_client: AsyncClient,
    occlusion_mask_session: AsyncSession,
    user_idx: Union[int, None],
    cam_idx: Union[int, None],
    pose_id: int,
    status_code: int,
    expected_count: Union[int, None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )
    elif isinstance(cam_idx, int):
        auth = pytest.get_token(
            pytest.camera_table[cam_idx]["id"],
            ["camera"],
            pytest.camera_table[cam_idx]["organization_id"],
        )

    response = await async_client.get(f"/poses/{pose_id}/occlusion_masks", headers=auth)

    assert response.status_code == status_code, print(response.__dict__)

    if status_code == 200:
        assert isinstance(response.json(), list)
        assert len(response.json()) == expected_count
