from datetime import datetime, timedelta
from typing import Any, Dict, List, Union

import pandas as pd
import pytest  # type: ignore
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints.sequences import _refresh_alert_state
from app.crud import AlertCRUD
from app.models import Alert, AlertSequence, Camera, Detection, Sequence
from app.schemas.sequences import SequenceLabel
from app.services.overlap import compute_overlap


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


@pytest.mark.asyncio
async def test_get_sequence_access_control(async_client: AsyncClient, sequence_session: AsyncSession):
    agent_auth = pytest.get_token(
        pytest.user_table[1]["id"], pytest.user_table[1]["role"].split(), pytest.user_table[1]["organization_id"]
    )
    response = await async_client.get("/sequences/1", headers=agent_auth)
    assert response.status_code == 200, response.text
    assert response.json()["id"] == 1

    response = await async_client.get("/sequences/2", headers=agent_auth)
    assert response.status_code == 403, response.text
    assert response.json()["detail"] == "Access forbidden."


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
        assert all(isinstance(elt["sequence_azimuth"], float) for elt in response.json())
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
        assert all(isinstance(elt["sequence_azimuth"], float) for elt in response.json())
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
        camera_azimuth=180.0,
        sequence_azimuth=170.0,
        cone_angle=5.0,
        is_wildfire=None,
        started_at=now - timedelta(seconds=30),
        last_seen_at=now - timedelta(seconds=20),
    )
    seq2 = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=182.0,
        sequence_azimuth=172.0,
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
        camera_azimuth=45.0,
        sequence_azimuth=40.0,
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


@pytest.mark.asyncio
async def test_latest_sequences_returns_recent_unlabeled(async_client: AsyncClient, sequence_session: AsyncSession):
    camera = await sequence_session.get(Camera, 1)
    other_camera = await sequence_session.get(Camera, 2)
    assert camera is not None
    assert other_camera is not None
    now = datetime.utcnow()
    seq_old = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=30.0,
        sequence_azimuth=25.0,
        cone_angle=4.0,
        is_wildfire=None,
        started_at=now - timedelta(hours=2),
        last_seen_at=now - timedelta(hours=2, minutes=50),
    )
    seq_new = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=32.0,
        sequence_azimuth=27.0,
        cone_angle=4.0,
        is_wildfire=None,
        started_at=now - timedelta(hours=1),
        last_seen_at=now - timedelta(minutes=30),
    )
    seq_labeled = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=34.0,
        sequence_azimuth=29.0,
        cone_angle=4.0,
        is_wildfire="wildfire_smoke",
        started_at=now - timedelta(hours=1),
        last_seen_at=now - timedelta(minutes=20),
    )
    seq_other_org = Sequence(
        camera_id=other_camera.id,
        pose_id=None,
        camera_azimuth=40.0,
        sequence_azimuth=35.0,
        cone_angle=4.0,
        is_wildfire=None,
        started_at=now - timedelta(hours=1),
        last_seen_at=now - timedelta(minutes=10),
    )
    sequence_session.add(seq_old)
    sequence_session.add(seq_new)
    sequence_session.add(seq_labeled)
    sequence_session.add(seq_other_org)
    await sequence_session.commit()
    await sequence_session.refresh(seq_old)
    await sequence_session.refresh(seq_new)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    response = await async_client.get("/sequences/unlabeled/latest", headers=auth)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert [item["id"] for item in payload] == [seq_new.id, seq_old.id]
    assert all(item["is_wildfire"] is None for item in payload)


@pytest.mark.asyncio
async def test_fetch_sequences_from_date_limit_offset(async_client: AsyncClient, sequence_session: AsyncSession):
    camera = await sequence_session.get(Camera, 1)
    other_camera = await sequence_session.get(Camera, 2)
    assert camera is not None
    assert other_camera is not None
    base = datetime.utcnow().replace(hour=10, minute=0, second=0, microsecond=0)
    seq_newest = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=50.0,
        sequence_azimuth=45.0,
        cone_angle=6.0,
        is_wildfire=None,
        started_at=base + timedelta(minutes=20),
        last_seen_at=base + timedelta(minutes=25),
    )
    seq_middle = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=55.0,
        sequence_azimuth=50.0,
        cone_angle=6.0,
        is_wildfire=None,
        started_at=base + timedelta(minutes=10),
        last_seen_at=base + timedelta(minutes=15),
    )
    seq_oldest = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=60.0,
        sequence_azimuth=55.0,
        cone_angle=6.0,
        is_wildfire=None,
        started_at=base,
        last_seen_at=base + timedelta(minutes=5),
    )
    seq_other_org = Sequence(
        camera_id=other_camera.id,
        pose_id=None,
        camera_azimuth=65.0,
        sequence_azimuth=60.0,
        cone_angle=6.0,
        is_wildfire=None,
        started_at=base + timedelta(minutes=12),
        last_seen_at=base + timedelta(minutes=18),
    )
    sequence_session.add(seq_newest)
    sequence_session.add(seq_middle)
    sequence_session.add(seq_oldest)
    sequence_session.add(seq_other_org)
    await sequence_session.commit()
    await sequence_session.refresh(seq_middle)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    date_str = base.date().isoformat()
    response = await async_client.get(f"/sequences/all/fromdate?from_date={date_str}&limit=1&offset=1", headers=auth)
    assert response.status_code == 200, response.text
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["id"] == seq_middle.id


@pytest.mark.asyncio
async def test_label_sequence_creates_alert_without_links(async_client: AsyncClient, detection_session: AsyncSession):
    camera = await detection_session.get(Camera, 1)
    assert camera is not None
    now = datetime.utcnow()
    seq = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=45.0,
        sequence_azimuth=40.0,
        cone_angle=10.0,
        is_wildfire=None,
        started_at=now - timedelta(minutes=5),
        last_seen_at=now - timedelta(minutes=4),
    )
    detection_session.add(seq)
    await detection_session.commit()
    await detection_session.refresh(seq)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.patch(
        f"/sequences/{seq.id}/label",
        json={"is_wildfire": SequenceLabel(is_wildfire="other_smoke").is_wildfire},
        headers=auth,
    )
    assert resp.status_code == 200, resp.text

    alerts_res = await detection_session.exec(select(Alert).execution_options(populate_existing=True))
    alerts = alerts_res.all()
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.started_at == seq.started_at
    assert alert.last_seen_at == seq.last_seen_at
    assert alert.lat is None
    assert alert.lon is None

    mappings_res = await detection_session.exec(select(AlertSequence).execution_options(populate_existing=True))
    mappings = mappings_res.all()
    assert len(mappings) == 1
    assert mappings[0].alert_id == alert.id
    assert mappings[0].sequence_id == seq.id


@pytest.mark.asyncio
async def test_delete_sequence_refreshes_alert_state(async_client: AsyncClient, detection_session: AsyncSession):
    camera = await detection_session.get(Camera, 1)
    assert camera is not None
    now = datetime.utcnow()
    seqs: List[Sequence] = []
    for idx, az in enumerate([30.0, 35.0, 40.0]):
        seq = Sequence(
            camera_id=camera.id,
            pose_id=None,
            camera_azimuth=az,
            sequence_azimuth=az,
            cone_angle=12.0,
            is_wildfire=None,
            started_at=now - timedelta(seconds=40 - idx * 10),
            last_seen_at=now - timedelta(seconds=30 - idx * 5),
        )
        detection_session.add(seq)
        seqs.append(seq)
    await detection_session.commit()
    for seq in seqs:
        await detection_session.refresh(seq)

    alert = Alert(
        organization_id=camera.organization_id,
        lat=None,
        lon=None,
        started_at=min(seq.started_at for seq in seqs),
        last_seen_at=max(seq.last_seen_at for seq in seqs),
    )
    detection_session.add(alert)
    await detection_session.commit()
    await detection_session.refresh(alert)
    for seq in seqs:
        detection_session.add(AlertSequence(alert_id=alert.id, sequence_id=seq.id))
    await detection_session.commit()

    detection = Detection(
        camera_id=camera.id,
        pose_id=None,
        sequence_id=seqs[0].id,
        azimuth=45.0,
        bucket_key="tmp-refresh",
        bboxes="[(0.1,0.1,0.2,0.2,0.9)]",
        created_at=now,
    )
    detection_session.add(detection)
    await detection_session.commit()
    await detection_session.refresh(detection)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.delete(f"/sequences/{seqs[0].id}", headers=auth)
    assert resp.status_code == 200, resp.text

    det_res = await detection_session.exec(
        select(Detection).where(Detection.id == detection.id).execution_options(populate_existing=True)
    )
    det = det_res.one()
    assert det.sequence_id is None

    remaining = seqs[1:]
    records = [
        {
            "id": seq.id,
            "lat": camera.lat,
            "lon": camera.lon,
            "sequence_azimuth": seq.sequence_azimuth,
            "cone_angle": seq.cone_angle,
            "is_wildfire": seq.is_wildfire,
            "started_at": seq.started_at,
            "last_seen_at": seq.last_seen_at,
        }
        for seq in remaining
    ]
    df = compute_overlap(pd.DataFrame.from_records(records))
    expected_loc = next((loc for locs in df["event_smoke_locations"].tolist() for loc in locs if loc is not None), None)

    alerts_res = await detection_session.exec(select(Alert).execution_options(populate_existing=True))
    alerts = alerts_res.all()
    assert len(alerts) == 1
    updated_alert = alerts[0]
    assert updated_alert.started_at == min(seq.started_at for seq in remaining)
    assert updated_alert.last_seen_at == max(seq.last_seen_at for seq in remaining)
    if expected_loc:
        assert updated_alert.lat == pytest.approx(expected_loc[0])
        assert updated_alert.lon == pytest.approx(expected_loc[1])
    else:
        assert updated_alert.lat is None
        assert updated_alert.lon is None


@pytest.mark.asyncio
async def test_refresh_alert_state_deletes_empty_alert(sequence_session: AsyncSession):
    camera = await sequence_session.get(Camera, 1)
    assert camera is not None
    now = datetime.utcnow()
    alert = Alert(
        organization_id=camera.organization_id,
        lat=None,
        lon=None,
        started_at=now,
        last_seen_at=now,
    )
    sequence_session.add(alert)
    await sequence_session.commit()
    await sequence_session.refresh(alert)

    await _refresh_alert_state(alert.id, sequence_session, AlertCRUD(sequence_session))

    alert_res = await sequence_session.exec(select(Alert).where(Alert.id == alert.id))
    assert alert_res.one_or_none() is None


@pytest.mark.asyncio
async def test_refresh_alert_state_updates_alert(sequence_session: AsyncSession):
    camera = await sequence_session.get(Camera, 1)
    assert camera is not None
    now = datetime.utcnow()
    seq1 = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=10.0,
        sequence_azimuth=10.0,
        cone_angle=20.0,
        is_wildfire=None,
        started_at=now - timedelta(seconds=40),
        last_seen_at=now - timedelta(seconds=30),
    )
    seq2 = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=12.0,
        sequence_azimuth=12.0,
        cone_angle=20.0,
        is_wildfire=None,
        started_at=now - timedelta(seconds=20),
        last_seen_at=now - timedelta(seconds=10),
    )
    sequence_session.add(seq1)
    sequence_session.add(seq2)
    await sequence_session.commit()
    await sequence_session.refresh(seq1)
    await sequence_session.refresh(seq2)

    alert = Alert(
        organization_id=camera.organization_id,
        lat=None,
        lon=None,
        started_at=now - timedelta(minutes=5),
        last_seen_at=now - timedelta(minutes=5),
    )
    sequence_session.add(alert)
    await sequence_session.commit()
    await sequence_session.refresh(alert)
    sequence_session.add(AlertSequence(alert_id=alert.id, sequence_id=seq1.id))
    sequence_session.add(AlertSequence(alert_id=alert.id, sequence_id=seq2.id))
    await sequence_session.commit()

    records = [
        {
            "id": seq.id,
            "lat": camera.lat,
            "lon": camera.lon,
            "sequence_azimuth": seq.sequence_azimuth,
            "cone_angle": seq.cone_angle,
            "is_wildfire": seq.is_wildfire,
            "started_at": seq.started_at,
            "last_seen_at": seq.last_seen_at,
        }
        for seq in (seq1, seq2)
    ]
    df = compute_overlap(pd.DataFrame.from_records(records))
    expected_loc = next((loc for locs in df["event_smoke_locations"].tolist() for loc in locs if loc is not None), None)

    await _refresh_alert_state(alert.id, sequence_session, AlertCRUD(sequence_session))

    alert_res = await sequence_session.exec(
        select(Alert).where(Alert.id == alert.id).execution_options(populate_existing=True)
    )
    updated = alert_res.one()
    assert updated.started_at == min(seq.started_at for seq in (seq1, seq2))
    assert updated.last_seen_at == max(seq.last_seen_at for seq in (seq1, seq2))
    if expected_loc:
        assert updated.lat == pytest.approx(expected_loc[0])
        assert updated.lon == pytest.approx(expected_loc[1])
    else:
        assert updated.lat is None
        assert updated.lon is None
