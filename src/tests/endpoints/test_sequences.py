from datetime import datetime, timedelta
from typing import Any, Dict, List, Union

import pytest  # type: ignore
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Alert, AlertSequence, Camera, Detection, Sequence
from app.schemas.sequences import SequenceLabel


@pytest.mark.parametrize(
    ("user_idx", "sequence_id", "status_code", "status_detail", "expected_result"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 1, 200, None, pytest.detection_table[:3][::-1]),
        (0, 2, 200, None, pytest.detection_table[3:4]),
        (0, 99, 404, "Table Sequence has no corresponding entry.", None),
        (1, 1, 200, None, pytest.detection_table[:3][::-1]),
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
    if status_code // 100 == 2:
        # Fetch the detection IDs to check that they are unset
        response = await async_client.get(f"/sequences/{sequence_id}/detections", headers=auth)
        det_ids = [det["id"] for det in response.json()]

    response = await async_client.delete(f"/sequences/{sequence_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None
        # Check that the detections are unset
        for det_id in det_ids:
            response = await async_client.get(f"/detections/{det_id}", headers=auth)
            assert response.json()["sequence_id"] is None


@pytest.mark.parametrize(
    ("user_idx", "sequence_id", "payload", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, {"is_wildfire": "wildfire_smoke"}, 401, "Not authenticated", None),
        (0, 0, {"is_wildfire": "wildfire_smoke"}, 422, None, None),
        (0, 99, {"is_wildfire": "wildfire_smoke"}, 404, None, None),
        (0, 1, {"label": "wildfire_smoke"}, 422, None, None),
        (0, 1, {"is_wildfire": "hello"}, 422, None, None),
        # (0, 1, {"is_wildfire": "True"}, 422, None, None),  # odd, this works
        (0, 1, {"is_wildfire": "wildfire_smoke"}, 200, None, 0),
        (0, 2, {"is_wildfire": "wildfire_smoke"}, 200, None, 1),
        (1, 1, {"is_wildfire": "wildfire_smoke"}, 200, None, 0),
        (1, 2, {"is_wildfire": "wildfire_smoke"}, 403, None, None),
        (2, 1, {"is_wildfire": "wildfire_smoke"}, 403, None, None),
        (2, 2, {"is_wildfire": "wildfire_smoke"}, 403, None, None),  # User cannot label
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
    detection_session: AsyncSession,
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
        assert all(isinstance(elt["cone_azimuth"], float) for elt in response.json())
        assert all(isinstance(elt["cone_angle"], float) for elt in response.json())


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
        assert all(isinstance(elt["cone_azimuth"], float) for elt in response.json())
        assert all(isinstance(elt["cone_angle"], float) for elt in response.json())


@pytest.mark.asyncio
async def test_sequence_label_updates_alerts(async_client: AsyncClient, detection_session: AsyncSession):
    # Create a sequence linked to a camera and an alert
    camera = await detection_session.get(Camera, 1)
    assert camera is not None
    now = datetime.utcnow()
    seq1 = Sequence(
        camera_id=camera.id,
        pose_id=None,
        azimuth=180.0,
        cone_azimuth=170.0,
        cone_angle=5.0,
        is_wildfire=None,
        started_at=now - timedelta(seconds=30),
        last_seen_at=now - timedelta(seconds=20),
    )
    seq2 = Sequence(
        camera_id=camera.id,
        pose_id=None,
        azimuth=182.0,
        cone_azimuth=172.0,
        cone_angle=5.0,
        is_wildfire=None,
        started_at=now - timedelta(seconds=25),
        last_seen_at=now - timedelta(seconds=10),
    )
    detection_session.add(seq1)
    detection_session.add(seq2)
    await detection_session.commit()
    await detection_session.refresh(seq1)
    await detection_session.refresh(seq2)

    alert = Alert(
        organization_id=camera.organization_id,
        lat=1.0,
        lon=2.0,
        started_at=min(seq1.started_at, seq2.started_at),
        last_seen_at=max(seq1.last_seen_at, seq2.last_seen_at),
    )
    detection_session.add(alert)
    await detection_session.commit()
    await detection_session.refresh(alert)
    detection_session.add(AlertSequence(alert_id=alert.id, sequence_id=seq1.id))
    detection_session.add(AlertSequence(alert_id=alert.id, sequence_id=seq2.id))
    await detection_session.commit()

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )

    # Keep original timings to avoid accessing expired ORM objects
    seq1_start, seq1_last = seq1.started_at, seq1.last_seen_at
    seq2_start, seq2_last = seq2.started_at, seq2.last_seen_at

    resp = await async_client.patch(
        f"/sequences/{seq1.id}/label",
        json={"is_wildfire": SequenceLabel(is_wildfire="other_smoke").is_wildfire},
        headers=auth,
    )
    assert resp.status_code == 200, resp.text

    alerts_res = await detection_session.exec(select(Alert).execution_options(populate_existing=True))
    alerts_rows = alerts_res.all()
    assert len(alerts_rows) == 2
    mappings_res = await detection_session.exec(
        select(AlertSequence.alert_id, AlertSequence.sequence_id).execution_options(populate_existing=True)
    )
    mappings = {(aid, sid) for aid, sid in mappings_res.all()}

    row_by_id = {row.id: row for row in alerts_rows}
    new_alert_row = next(row for aid, row in row_by_id.items() if aid != alert.id)
    updated_alert_row = row_by_id[alert.id]

    assert (new_alert_row.id, seq1.id) in mappings
    assert (updated_alert_row.id, seq1.id) not in mappings
    assert (updated_alert_row.id, seq2.id) in mappings

    assert updated_alert_row.started_at == seq2_start
    assert updated_alert_row.last_seen_at == seq2_last
    assert updated_alert_row.lat is None
    assert updated_alert_row.lon is None

    assert new_alert_row.started_at == seq1_start
    assert new_alert_row.last_seen_at == seq1_last
    assert new_alert_row.lat is None
    assert new_alert_row.lon is None


@pytest.mark.asyncio
async def test_delete_sequence_cleans_alerts_and_detections(async_client: AsyncClient, detection_session: AsyncSession):
    camera = await detection_session.get(Camera, 1)
    assert camera is not None
    now = datetime.utcnow()
    seq = Sequence(
        camera_id=camera.id,
        pose_id=None,
        azimuth=45.0,
        cone_azimuth=40.0,
        cone_angle=10.0,
        is_wildfire=None,
        started_at=now,
        last_seen_at=now,
    )
    detection = Detection(
        camera_id=camera.id,
        pose_id=None,
        sequence_id=None,
        azimuth=45.0,
        bucket_key="tmp",
        bboxes="[(0.1,0.1,0.2,0.2,0.9)]",
        created_at=now,
    )
    detection_session.add(seq)
    detection_session.add(detection)
    await detection_session.commit()
    await detection_session.refresh(seq)
    await detection_session.refresh(detection)

    alert = Alert(
        organization_id=camera.organization_id,
        lat=None,
        lon=None,
        started_at=now,
        last_seen_at=now,
    )
    detection_session.add(alert)
    await detection_session.commit()
    await detection_session.refresh(alert)
    detection_session.add(AlertSequence(alert_id=alert.id, sequence_id=seq.id))
    await detection_session.commit()

    # Link detection to sequence
    detection.sequence_id = seq.id
    detection_session.add(detection)
    await detection_session.commit()

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.delete(f"/sequences/{seq.id}", headers=auth)
    assert resp.status_code == 200, resp.text

    # Alert and mapping should be gone
    mappings_res = await detection_session.exec(select(AlertSequence))
    assert mappings_res.all() == []
    alerts_res = await detection_session.exec(select(Alert))
    assert alerts_res.all() == []

    # Detection should have sequence_id cleared
    det_res = await detection_session.exec(
        select(Detection).where(Detection.id == detection.id).execution_options(populate_existing=True)
    )
    det = det_res.one()
    assert det.sequence_id is None
