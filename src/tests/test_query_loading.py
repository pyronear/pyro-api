import csv
import io
from datetime import timedelta

import pytest
from sqlalchemy import event

from app.core.time import utcnow
from app.crud import DetectionCRUD
from app.db import engine
from app.models import Alert, AlertSequence, Camera, Detection, Pose, Sequence


@pytest.mark.parametrize("camera_count", [1, 20])
@pytest.mark.asyncio
async def test_camera_list_loads_active_poses_with_one_query(async_client, camera_session, camera_count):
    cameras = [
        Camera(name=f"batch-camera-{i}", organization_id=1, lat=48, lon=2, elevation=10, angle_of_view=90)
        for i in range(camera_count)
    ]
    camera_session.add_all(cameras)
    await camera_session.flush()
    for camera in cameras:
        camera_session.add_all([
            Pose(camera_id=camera.id, azimuth=10, active=True),
            Pose(camera_id=camera.id, azimuth=20, active=False),
        ])
    await camera_session.commit()
    queries = []

    def capture(_conn, _cursor, statement, _params, _context, _many):
        if statement.startswith("SELECT") and "FROM poses" in statement:
            queries.append(statement)

    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        response = await async_client.get("/cameras", headers=pytest.get_token(1, ["admin"], 1))
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert response.status_code == 200, response.text
    by_id = {camera["id"]: camera for camera in response.json()}
    for camera in cameras:
        assert len(by_id[camera.id]["poses"]) == 1
        assert by_id[camera.id]["poses"][0]["camera_id"] == camera.id
    assert len(queries) == 1


@pytest.mark.asyncio
async def test_latest_bbox_batch_skips_continuity_and_breaks_timestamp_ties(sequence_session):
    now = utcnow()
    rows = [
        Detection(camera_id=1, pose_id=1, sequence_id=1, bucket_key="older", bbox="[(.1,.1,.2,.2,.1)]", created_at=now),
        Detection(camera_id=1, pose_id=1, sequence_id=1, bucket_key="newer", bbox="[(.2,.2,.3,.3,.9)]", created_at=now),
        Detection(
            camera_id=1, pose_id=1, sequence_id=1, bucket_key="empty", bbox="[]", created_at=now + timedelta(seconds=1)
        ),
        Detection(camera_id=2, pose_id=3, sequence_id=2, bucket_key="only-empty", bbox="[]", created_at=now),
    ]
    sequence_session.add_all(rows)
    await sequence_session.commit()
    latest = await DetectionCRUD(sequence_session).get_latest_bboxes([1, 2])
    assert set(latest) == {1}
    assert latest[1].bucket_key == "newer"
    assert await DetectionCRUD(sequence_session).get_latest_bboxes([]) == {}


@pytest.mark.asyncio
async def test_frame_window_hydrates_only_recent_distinct_keys(sequence_session):
    now = utcnow()
    rows = [
        Detection(
            camera_id=1,
            pose_id=1,
            sequence_id=1,
            bucket_key=f"frame-{i}",
            bbox="[]",
            created_at=now + timedelta(seconds=i),
        )
        for i in range(100)
    ]
    rows.extend([
        Detection(
            camera_id=1,
            pose_id=1,
            sequence_id=1,
            bucket_key="frame-99",
            bbox="[(.1,.1,.2,.2,.9)]",
            created_at=now + timedelta(seconds=101),
        ),
        # A later bbox for an old frame must not move that frame to the recent window.
        Detection(
            camera_id=1,
            pose_id=1,
            sequence_id=1,
            bucket_key="frame-0",
            bbox="[]",
            created_at=now + timedelta(seconds=102),
        ),
    ])
    sequence_session.add_all(rows)
    await sequence_session.commit()
    total, frames, hydrated = await DetectionCRUD(sequence_session).fetch_frame_window(1, 10)
    assert total == 100
    assert frames == [f"frame-{i}" for i in range(90, 100)]
    assert len(hydrated) == 11
    assert {row.bucket_key for row in hydrated} == set(frames)


@pytest.mark.parametrize(("scope", "expected_count"), [("admin", 5), ("agent", 4)])
@pytest.mark.asyncio
async def test_csv_stream_pages_across_ties_and_one_large_alert(
    async_client, camera_session, monkeypatch, scope, expected_count
):
    from app.api.api_v1.endpoints import alerts as endpoint

    now = utcnow().replace(microsecond=0)
    alerts = [Alert(organization_id=org, started_at=now, last_seen_at=now) for org in [1, 1, 2]]
    camera_session.add_all(alerts)
    await camera_session.flush()
    pairs = []
    for alert, count in zip(alerts, [3, 1, 1], strict=True):
        for _ in range(count):
            sequence = Sequence(camera_id=alert.organization_id, camera_azimuth=45, started_at=now, last_seen_at=now)
            camera_session.add(sequence)
            await camera_session.flush()
            camera_session.add(AlertSequence(alert_id=alert.id, sequence_id=sequence.id))
            pairs.append((alert.id, sequence.id))
    await camera_session.commit()
    monkeypatch.setattr(endpoint, "_ALERT_EXPORT_BATCH_SIZE", 2)
    query_limits = []

    def capture(_conn, _cursor, statement, params, _context, _many):
        if statement.startswith("SELECT") and "FROM alerts" in statement:
            assert "LIMIT" in statement
            query_limits.append(params[-1])

    event.listen(engine.sync_engine, "before_cursor_execute", capture)
    try:
        response = await async_client.get(
            "/alerts/export",
            headers=pytest.get_token(1, [scope], 1),
            params={"from_date": now.date().isoformat(), "to_date": now.date().isoformat()},
        )
    finally:
        event.remove(engine.sync_engine, "before_cursor_execute", capture)
    assert response.status_code == 200, response.text
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == expected_count
    assert [(int(row["alert_id"]), int(row["sequence_id"])) for row in rows] == pairs[:expected_count]
    assert response.text.count("alert_id,") == 1
    assert len(query_limits) == 3
    assert query_limits == [2, 2, 2]


@pytest.mark.parametrize(("scope", "expected_ids"), [("admin", [1, 2, 3, 4]), ("user", [1, 2, 3])])
@pytest.mark.asyncio
async def test_detection_pagination_applies_organization_filter_before_offset(
    async_client, detection_session, scope, expected_ids
):
    auth = pytest.get_token(1, [scope], 1)
    pages = []
    for offset in range(0, len(expected_ids), 2):
        response = await async_client.get("/detections", headers=auth, params={"limit": 2, "offset": offset})
        assert response.status_code == 200, response.text
        pages.extend(row["id"] for row in response.json())
    assert pages == expected_ids


@pytest.mark.asyncio
async def test_detection_default_page_is_bounded_and_remainder_is_accessible(async_client, detection_session):
    detection_session.add_all([
        Detection(camera_id=1, pose_id=1, bucket_key=f"page-frame-{i}", bbox="[]") for i in range(101)
    ])
    await detection_session.commit()
    auth = pytest.get_token(1, ["admin"], 1)
    first = await async_client.get("/detections", headers=auth)
    second = await async_client.get("/detections", headers=auth, params={"offset": 100})
    assert first.status_code == second.status_code == 200
    assert len(first.json()) == 100
    assert len(second.json()) == 5
    assert [row["id"] for row in first.json() + second.json()] == list(range(1, 106))


@pytest.mark.parametrize(
    ("endpoint", "query"),
    [
        ("/detections", "limit=501"),
        ("/detections", "limit=0"),
        ("/detections", "offset=-1"),
        ("/alerts/unlabeled/latest", "limit=101"),
        ("/alerts/unlabeled/latest", "offset=-1"),
        ("/alerts/all/fromdate", "from_date=2026-10-10&limit=101"),
        ("/sequences/all/fromdate", "from_date=2026-10-10&limit=101"),
        ("/sequences/all/fromdate", "from_date=2026-10-10&offset=-1"),
    ],
)
@pytest.mark.asyncio
async def test_list_endpoints_reject_unbounded_or_negative_pages(async_client, endpoint, query):
    response = await async_client.get(f"{endpoint}?{query}", headers=pytest.get_token(1, ["admin"], 1))
    assert response.status_code == 422
