from typing import Any, Dict, List, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "cam_idx", "payload", "status_code", "status_detail"),
    [
        (
            None,
            None,
            {"camera_id": "2", "azimuth": 43.7, "starting_time": "2023-12-10T15:08:19.226673", "ending_time": None},
            401,
            "Not authenticated",
        ),
        (
            1,
            None,
            {"camera_id": "2", "azimuth": 43.7, "starting_time": "2023-12-11T15:08:19.226673", "ending_time": None},
            403,
            "Incompatible token scope.",
        ),
        (
            None,
            0,
            {"camera_id": "1", "azimuth": 43.7, "starting_time": "2023-12-09T15:08:19.226673", "ending_time": None},
            409,
            "Unclosed Wildfire in the database.",
        ),
        (
            None,
            1,
            {"camera_id": "2", "azimuth": 43.7, "starting_time": "2023-12-12T15:08:19.226673", "ending_time": None},
            201,
            None,
        ),
    ],
)
@pytest.mark.asyncio()
async def test_create_wildfire(
    async_client: AsyncClient,
    wildfire_session: AsyncSession,
    user_idx: Union[int, None],
    cam_idx: Union[int, None],
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
    elif isinstance(cam_idx, int):
        auth = pytest.get_token(
            pytest.camera_table[cam_idx]["id"],
            ["camera"],
            pytest.camera_table[cam_idx]["organization_id"],
        )

    response = await async_client.post("/wildfires", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail


@pytest.mark.parametrize(
    ("user_idx", "organisation_id", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 1, 200, None, 0),
        (1, 1, 200, None, 0),
        (2, 1, 403, "Access forbidden.", 0),
    ],
)
@pytest.mark.asyncio()
async def test_get_wildfire(
    async_client: AsyncClient,
    wildfire_session: AsyncSession,
    user_idx: Union[int, None],
    organisation_id: int,
    status_code: int,
    status_detail: Union[str, None],
    expected_idx: Union[int, None],
):
    auth = None
    organisation_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organisation_id_from_table,
        )

    response = await async_client.get(f"/wildfires/{1}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.wildfire_table[expected_idx]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_response"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, pytest.wildfire_table),
        (1, 200, None, [pytest.wildfire_table[0], pytest.wildfire_table[1]]),
        (2, 200, None, [pytest.wildfire_table[2]]),
    ],
)
@pytest.mark.asyncio()
async def test_fetch_wildfires(
    async_client: AsyncClient,
    wildfire_session: AsyncSession,
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

    response = await async_client.get("/wildfires", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == expected_response


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail"),
    [
        (None, 401, "Not authenticated"),
        (0, 200, None),
        (1, 200, None),
        (2, 403, "Access forbidden."),
    ],
)
@pytest.mark.asyncio()
async def test_delete_wildfire(
    async_client: AsyncClient,
    wildfire_session: AsyncSession,
    user_idx: Union[int, None],
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

    response = await async_client.delete(f"/wildfires/{1}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None


@pytest.mark.parametrize(
    ("user_idx", "payload", "status_code", "status_detail", "get_response"),
    [
        (
            None,
            {"id": "1", "ending_time": "2023-12-15T15:08:19.226673"},
            401,
            "Not authenticated",
            {
                "starting_time": "2023-12-07T15:08:19.226673",
                "id": 2,
                "camera_id": 1,
                "azimuth": 43.7,
                "ending_time": None,
            },
        ),
        (
            0,
            {"id": "1", "ending_time": "2023-12-15T15:08:19.226673"},
            200,
            None,
            {
                "starting_time": "2023-12-07T15:08:19.226673",
                "id": 2,
                "camera_id": 1,
                "azimuth": 43.7,
                "ending_time": "2023-12-15T15:08:19.226673",
            },
        ),
        (
            1,
            {"id": "1", "ending_time": "2023-12-15T15:08:19.226673"},
            200,
            None,
            {
                "starting_time": "2023-12-07T15:08:19.226673",
                "id": 2,
                "camera_id": 1,
                "azimuth": 43.7,
                "ending_time": "2023-12-15T15:08:19.226673",
            },
        ),
        (
            2,
            {"id": "1", "ending_time": "2023-12-15T15:08:19.226673"},
            403,
            "Incompatible token scope.",
            {
                "starting_time": "2023-12-07T15:08:19.226673",
                "id": 2,
                "camera_id": 1,
                "azimuth": 43.7,
                "ending_time": None,
            },
        ),
    ],
)
@pytest.mark.asyncio()
async def test_update_wildfire(
    async_client: AsyncClient,
    wildfire_session: AsyncSession,
    user_idx: Union[int, None],
    payload: str,
    status_code: int,
    status_detail: Union[str, None],
    get_response: str,
):
    auth = None
    organization_id_from_table = pytest.user_table[user_idx]["organization_id"] if user_idx is not None else None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            organization_id_from_table,
        )

    response = await async_client.patch(f"/wildfires/{2}", json=payload, headers=auth)

    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None

    auth = pytest.get_token(
        pytest.user_table[0]["id"],
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )
    response = await async_client.get(f"/wildfires/{2}", headers=auth)

    assert response.json() == get_response
