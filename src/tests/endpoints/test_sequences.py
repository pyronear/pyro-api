from typing import Any, Dict, List, Union

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession


@pytest.mark.parametrize(
    ("user_idx", "sequence_id", "status_code", "status_detail", "expected_result"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 1, 200, None, pytest.detection_table[:3]),
        (0, 2, 200, None, pytest.detection_table[3:4]),
        (0, 99, 404, "Table Sequence has no corresponding entry.", None),
        (1, 1, 200, None, pytest.detection_table[:3]),
        (1, 2, 403, "Access forbidden.", None),
        (2, 1, 403, "Access forbidden.", None),
        (2, 2, 200, None, pytest.detection_table[3:4]),
    ],
)
@pytest.mark.asyncio
async def test_fetch_sequence_detections(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    user_idx: Union[int, None],
    sequence_id: int,
    status_code: int,
    status_detail: Union[str, None],
    expected_result: Union[List[Dict[str, Any]], None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get(f"/sequences/{sequence_id}/detections", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2 and expected_result is not None:
        assert [{k: v for k, v in det.items() if k != "url"} for det in response.json()] == expected_result
        assert all(det["url"].startswith("http://") for det in response.json())


@pytest.mark.parametrize(
    ("user_idx", "sequence_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 99, 404, "Table Sequence has no corresponding entry."),
        (0, 1, 200, None),
        (0, 2, 200, None),
        (1, 1, 403, "Incompatible token scope."),
        (1, 2, 403, "Incompatible token scope."),
        (2, 1, 403, "Incompatible token scope."),
        (2, 2, 403, "Incompatible token scope."),
    ],
)
@pytest.mark.asyncio
async def test_delete_sequence(
    async_client: AsyncClient,
    detection_session: AsyncSession,
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


@pytest.mark.parametrize(
    ("user_idx", "sequence_id", "payload", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, {"is_wildfire": True}, 401, "Not authenticated", None),
        (0, 0, {"is_wildfire": True}, 422, None, None),
        (0, 99, {"is_wildfire": True}, 404, None, None),
        (0, 1, {"label": True}, 422, None, None),
        (0, 1, {"is_wildfire": "hello"}, 422, None, None),
        # (0, 1, {"is_wildfire": "True"}, 422, None, None),  # odd, this works
        (0, 1, {"is_wildfire": True}, 200, None, 0),
        (0, 2, {"is_wildfire": True}, 200, None, 1),
        (1, 1, {"is_wildfire": True}, 200, None, 0),
        (1, 2, {"is_wildfire": True}, 403, None, None),
        (2, 1, {"is_wildfire": True}, 403, None, None),
        (2, 2, {"is_wildfire": True}, 403, None, None),  # User cannot label
    ],
)
@pytest.mark.asyncio
async def test_label_sequence(
    async_client: AsyncClient,
    sequence_session: AsyncSession,
    user_idx: Union[int, None],
    sequence_id: int,
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

    response = await async_client.patch(f"/sequences/{sequence_id}/label", json=payload, headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == {
            **{k: v for k, v in pytest.sequence_table[expected_idx].items() if k != "is_wildfire"},
            **payload,
        }


@pytest.mark.parametrize(
    ("user_idx", "from_date", "status_code", "status_detail", "expected_result"),
    [
        (None, "2018-06-06", 401, "Not authenticated", None),
        (0, "", 422, None, None),
        (0, "old-date", 422, None, None),
        (0, "2018-19-20", 422, None, None),  # impossible date
        (0, "2018-06-06T00:00:00", 200, None, []),  # datetime != date, weird, but works
        (0, "2018-06-06", 200, None, []),
        (0, "2023-11-07", 200, None, pytest.sequence_table[:1]),
        (1, "2023-11-07", 200, None, pytest.sequence_table[:1]),
        (2, "2023-11-07", 200, None, pytest.sequence_table[1:2]),
    ],
)
@pytest.mark.asyncio
async def test_fetch_sequences_from_date(
    async_client: AsyncClient,
    sequence_session: AsyncSession,
    user_idx: Union[int, None],
    from_date: str,
    status_code: int,
    status_detail: Union[str, None],
    expected_result: Union[List[Dict[str, Any]], None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get(f"/sequences/all/fromdate?from_date={from_date}", headers=auth)

    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == expected_result


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_result"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, []),
        (1, 200, None, []),
        (2, 200, None, []),
    ],
)
@pytest.mark.asyncio
async def test_latest_sequences(
    async_client: AsyncClient,
    sequence_session: AsyncSession,
    user_idx: Union[int, None],
    status_code: int,
    status_detail: Union[str, None],
    expected_result: Union[List[Dict[str, Any]], None],
):
    auth = None
    if isinstance(user_idx, int):
        auth = pytest.get_token(
            pytest.user_table[user_idx]["id"],
            pytest.user_table[user_idx]["role"].split(),
            pytest.user_table[user_idx]["organization_id"],
        )

    response = await async_client.get("/sequences/unlabeled/latest", headers=auth)

    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == expected_result
