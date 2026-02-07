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
            {"id": 1, "camera_id": 1, "azimuth": 45.0, "patrol_id": 1, "image": None, "image_url": None},
        ),
        (
            1,
            2,
            200,
            None,
            {"id": 2, "camera_id": 1, "azimuth": 90.0, "patrol_id": 1, "image": None, "image_url": None},
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
            {"id": 1, "camera_id": 1, "azimuth": 123.4, "patrol_id": 123, "image": None, "image_url": None},
        ),
        (
            1,
            2,
            {"patrol_id": 456},
            200,
            None,
            {"id": 2, "camera_id": 1, "azimuth": 90.0, "patrol_id": 456, "image": None, "image_url": None},
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
    ("cam_idx", "status_code", "expected_count"),
    [
        (0, 200, 2),
        (1, 200, 1),
    ],
)
@pytest.mark.asyncio
async def test_list_current_poses_camera(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    pose_session: AsyncSession,
    cam_idx: int,
    status_code: int,
    expected_count: int,
):
    auth = pytest.get_token(
        pytest.camera_table[cam_idx]["id"],
        ["camera"],
        pytest.camera_table[cam_idx]["organization_id"],
    )

    response = await async_client.get("/poses", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if response.status_code == 200:
        json_resp = response.json()
        assert isinstance(json_resp, list)
        assert len(json_resp) == expected_count
        assert {pose["camera_id"] for pose in json_resp} == {pytest.camera_table[cam_idx]["id"]}


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


@pytest.mark.parametrize(
    ("user_idx", "pose_id", "status_code"),
    [
        (0, 1, 200),  # Admin can access
        (1, 1, 200),  # Agent in same org can access
        (2, 1, 403),  # Agent in different org cannot access
    ],
)
@pytest.mark.asyncio
async def test_get_pose_with_image(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    pose_session: AsyncSession,
    user_idx: int,
    pose_id: int,
    status_code: int,
):
    """Test getting a pose returns image_url when image exists"""
    auth = pytest.get_token(
        pytest.user_table[user_idx]["id"],
        pytest.user_table[user_idx]["role"].split(),
        pytest.user_table[user_idx]["organization_id"],
    )

    response = await async_client.get(f"/poses/{pose_id}", headers=auth)
    assert response.status_code == status_code

    if status_code == 200:
        json_resp = response.json()
        assert "image" in json_resp
        assert "image_url" in json_resp
        # image_url should be None if no image exists, or a string if it does
        if json_resp["image"] is not None:
            assert isinstance(json_resp["image_url"], str)
        else:
            assert json_resp["image_url"] is None


@pytest.mark.parametrize(
    ("auth_type", "auth_idx", "pose_id", "status_code", "status_detail"),
    [
        (None, None, 1, 401, "Not authenticated"),
        ("camera", 0, 1, 200, None),  # Camera updating its own pose
        ("camera", 0, 3, 403, "Access forbidden."),  # Camera updating another camera's pose
        ("user", 0, 1, 200, None),  # Admin can update
        ("user", 1, 1, 200, None),  # Agent in same org can update
        ("user", 2, 1, 403, "Incompatible token scope."),  # Agent in different org cannot update
    ],
)
@pytest.mark.asyncio
async def test_update_pose_image(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    pose_session: AsyncSession,
    mock_img: bytes,
    auth_type: Union[str, None],
    auth_idx: Union[int, None],
    pose_id: int,
    status_code: int,
    status_detail: Union[str, None],
):
    """Test updating a pose image"""
    auth = None
    if auth_type == "camera":
        auth = pytest.get_token(
            pytest.camera_table[auth_idx]["id"],
            ["camera"],
            pytest.camera_table[auth_idx]["organization_id"],
        )
    elif auth_type == "user":
        auth = pytest.get_token(
            pytest.user_table[auth_idx]["id"],
            pytest.user_table[auth_idx]["role"].split(),
            pytest.user_table[auth_idx]["organization_id"],
        )

    response = await async_client.patch(
        f"/poses/{pose_id}/image",
        files={"file": ("test_image.png", mock_img, "image/png")},
        headers=auth,
    )

    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail

    if response.status_code // 100 == 2:
        json_resp = response.json()
        assert isinstance(json_resp["image"], str)
        assert json_resp["image"] != ""  # Should have a bucket key


@pytest.mark.asyncio
async def test_get_pose_after_image_upload(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    pose_session: AsyncSession,
    mock_img: bytes,
):
    """Test that getting a pose after uploading an image returns a valid image_url"""
    # Get admin token
    auth = pytest.get_token(
        pytest.user_table[0]["id"],  # Admin user
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )

    pose_id = 1

    # First, upload an image to the pose
    upload_response = await async_client.patch(
        f"/poses/{pose_id}/image",
        files={"file": ("test_image.png", mock_img, "image/png")},
        headers=auth,
    )
    assert upload_response.status_code == 200
    assert upload_response.json()["image"] is not None

    # Then, retrieve the pose and verify image_url is generated
    get_response = await async_client.get(f"/poses/{pose_id}", headers=auth)
    assert get_response.status_code == 200

    json_resp = get_response.json()
    assert "image" in json_resp
    assert "image_url" in json_resp
    # Verify image_url is a valid string (presigned S3 URL)
    assert isinstance(json_resp["image"], str)
    assert isinstance(json_resp["image_url"], str)
    assert json_resp["image_url"] is not None
    assert len(json_resp["image_url"]) > 0
    # Verify the URL contains expected S3 components
    assert "http" in json_resp["image_url"]  # Should be a valid URL
