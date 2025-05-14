from typing import Any, Dict, List, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            {
                "name": "pyro-cam",
                "organization_id": 1,
                "angle_of_view": 90.0,
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            401,
            "Not authenticated",
        ),
        (
            0,
            {"name": "pyro-cam", "organization_id": 1, "angle_of_view": 90.0, "elevation": 30.0, "lat": 3.5},
            422,
            None,
        ),
        (
            0,
            {
                "name": "pyro-cam",
                "organization_id": 1,
                "angle_of_view": 90.0,
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            201,
            None,
        ),
        (
            1,
            {
                "name": "pyro-cam",
                "organization_id": 1,
                "angle_of_view": 90.0,
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            201,
            None,
        ),
        (
            2,
            {
                "name": "pyro-cam",
                "organization_id": 2,
                "angle_of_view": 90.0,
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_camera(
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

    response = await async_client.post("/cameras", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert {
            k: v
            for k, v in response.json().items()
            if k not in {"id", "created_at", "last_active_at", "is_trustable", "last_image"}
        } == payload


@pytest.mark.parametrize(
    ("user_idx", "cam_id", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 0, 422, None, None),
        (0, 100, 404, "Table Camera has no corresponding entry.", None),
        (0, 1, 200, None, 0),
        (1, 1, 200, None, 0),
        (2, 1, 403, "Access forbidden.", 0),
    ],
)
@pytest.mark.asyncio
async def test_get_camera(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    user_idx: Union[int, None],
    cam_id: int,
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

    response = await async_client.get(f"/cameras/{cam_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.camera_table[expected_idx]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_response"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, pytest.camera_table[0]),
        (1, 200, None, pytest.camera_table[0]),
        (2, 200, None, pytest.camera_table[1]),
    ],
)
@pytest.mark.asyncio
async def test_fetch_cameras(
    async_client: AsyncClient,
    camera_session: AsyncSession,
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

    response = await async_client.get("/cameras", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json()[0] == expected_response


@pytest.mark.parametrize(
    ("user_idx", "cam_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 0, 422, None),
        (0, 100, 404, "Table Camera has no corresponding entry."),
        (0, 1, 200, None),
        (0, 2, 200, None),
        (1, 1, 403, "Incompatible token scope."),
        (1, 2, 403, "Incompatible token scope."),
        (2, 1, 403, "Incompatible token scope."),
        (2, 2, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_delete_camera(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    user_idx: Union[int, None],
    cam_id: int,
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

    response = await async_client.delete(f"/cameras/{cam_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None


@pytest.mark.parametrize(
    ("user_idx", "cam_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 0, 422, None),
        (0, 100, 404, "Table Camera has no corresponding entry."),
        (0, 1, 200, None),
        (1, 1, 403, "Incompatible token scope."),
        (2, 1, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_create_camera_token(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    user_idx: Union[int, None],
    cam_id: int,
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

    response = await async_client.post(f"/cameras/{cam_id}/token", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        response_json = response.json()
        assert response_json["token_type"] == "bearer"  # noqa: S105
        assert isinstance(response_json["access_token"], str)
        assert len(response_json["access_token"].split(".")) == 3


@pytest.mark.parametrize(
    ("cam_idx", "status_code", "status_detail"),
    [
        (None, 401, "Not authenticated"),
        (0, 200, None),
        (1, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_heartbeat(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    cam_idx: Union[int, None],
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    if isinstance(cam_idx, int):
        auth = pytest.get_token(
            pytest.camera_table[cam_idx]["id"],
            ["camera"],
            pytest.camera_table[cam_idx]["organization_id"],
        )

    response = await async_client.patch("/cameras/heartbeat", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert isinstance(response.json()["last_active_at"], str)
        if pytest.camera_table[cam_idx]["last_active_at"] is not None:
            assert response.json()["last_active_at"] > pytest.camera_table[cam_idx]["last_active_at"]
        assert {k: v for k, v in response.json().items() if k != "last_active_at"} == {
            k: v for k, v in pytest.camera_table[cam_idx].items() if k != "last_active_at"
        }


@pytest.mark.parametrize(
    ("cam_idx", "status_code", "status_detail"),
    [
        (None, 401, "Not authenticated"),
        (0, 200, None),
        (1, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_update_image(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    mock_img: bytes,
    cam_idx: Union[int, None],
    status_code: int,
    status_detail: Union[str, None],
):
    auth = None
    if isinstance(cam_idx, int):
        auth = pytest.get_token(
            pytest.camera_table[cam_idx]["id"],
            ["camera"],
            pytest.camera_table[cam_idx]["organization_id"],
        )

    response = await async_client.patch(
        "/cameras/image", files={"file": ("logo.png", mock_img, "image/png")}, headers=auth
    )
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert isinstance(response.json()["last_active_at"], str)
        if pytest.camera_table[cam_idx]["last_active_at"] is not None:
            assert response.json()["last_active_at"] > pytest.camera_table[cam_idx]["last_active_at"]
        assert isinstance(response.json()["last_image"], str)
        if pytest.camera_table[cam_idx]["last_image"] is not None:
            assert response.json()["last_image"] != pytest.camera_table[cam_idx]["last_image"]
        assert {k: v for k, v in response.json().items() if k not in {"last_active_at", "last_image"}} == {
            k: v for k, v in pytest.camera_table[cam_idx].items() if k not in {"last_active_at", "last_image"}
        }


@pytest.mark.parametrize(
    ("user_idx", "cam_id", "payload", "status_code", "status_detail"),
    [
        (
            None,
            1,
            {
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            401,
            "Not authenticated",
        ),
        (
            0,
            1,
            {"elevation": 30.0, "lat": 3.5},
            422,
            None,
        ),
        (
            0,
            999,
            {
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            404,
            "Table Camera has no corresponding entry.",
        ),
        (
            0,
            1,
            {
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            200,
            None,
        ),
        (
            0,
            2,
            {
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            200,
            None,
        ),
        (
            1,
            1,
            {
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            403,
            "Incompatible token scope.",
        ),
        (
            1,
            2,
            {
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            1,
            {
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            2,
            {
                "elevation": 30.0,
                "lat": 3.5,
                "lon": 7.8,
            },
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_camera_location(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    user_idx: Union[int, None],
    cam_id: int,
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

    response = await async_client.patch(f"/cameras/{cam_id}/location", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert {k: v for k, v in response.json().items() if k in {"lat", "lon", "elevation"}} == payload


@pytest.mark.parametrize(
    ("user_idx", "cam_id", "payload", "status_code", "status_detail"),
    [
        (
            None,
            1,
            {
                "name": "pyro-cam",
            },
            401,
            "Not authenticated",
        ),
        (
            0,
            1,
            {"name": "cam"},  # name too short
            422,
            None,
        ),
        (
            0,
            999,
            {
                "name": "pyro-cam",
            },
            404,
            "Table Camera has no corresponding entry.",
        ),
        (
            0,
            1,
            {
                "name": "pyro-cam",
            },
            200,
            None,
        ),
        (
            0,
            2,
            {
                "name": "pyro-cam",
            },
            200,
            None,
        ),
        (
            1,
            1,
            {
                "name": "pyro-cam",
            },
            403,
            "Incompatible token scope.",
        ),
        (
            1,
            2,
            {
                "name": "pyro-cam",
            },
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            1,
            {
                "name": "pyro-cam",
            },
            403,
            "Incompatible token scope.",
        ),
        (
            2,
            2,
            {
                "name": "pyro-cam",
            },
            403,
            "Incompatible token scope.",
        ),
    ],
)
@pytest.mark.asyncio
async def test_update_camera_name(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    user_idx: Union[int, None],
    cam_id: int,
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

    response = await async_client.patch(f"/cameras/{cam_id}/name", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert all(response.json()[k] == v for k, v in payload.items())
