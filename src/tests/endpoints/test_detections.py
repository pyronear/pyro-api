import asyncio
import io
from ast import literal_eval
from collections import Counter
from datetime import datetime, timedelta
from typing import Any, Dict, List, Union

import pytest  # type: ignore
from fastapi import BackgroundTasks, HTTPException, UploadFile
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints import detections as detections_api
from app.api.api_v1.endpoints.detections import (
    _attach_sequence_to_alert,
    _build_links_for_group,
    _build_overlap_records,
    _fetch_alert_mapping,
    _get_camera_by_id,
    _get_last_bbox_for_sequence,
    _get_or_create_alert_id,
    _get_recent_sequences,
    _maybe_update_alert,
    _parse_bbox,
    _resolve_groups_and_locations,
    create_detection,
)
from app.core.config import settings
from app.crud import AlertCRUD, CameraCRUD, DetectionCRUD, OrganizationCRUD, PoseCRUD, SequenceCRUD, WebhookCRUD
from app.models import Alert, AlertSequence, Camera, Detection, Organization, Pose, Role, Sequence, Webhook
from app.schemas.login import TokenPayload
from app.services.cones import resolve_cone


@pytest.mark.parametrize(
    ("user_idx", "cam_idx", "payload", "status_code", "status_detail", "repeat"),
    [
        (None, None, {"pose_id": 1, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 401, "Not authenticated", None),
        (0, None, {"pose_id": 1, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 403, "Incompatible token scope.", None),
        (1, None, {"pose_id": 1, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 403, "Incompatible token scope.", None),
        (2, None, {"pose_id": 1, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 403, "Incompatible token scope.", None),
        (None, 0, {}, 422, None, None),
        (None, 0, {"pose_id": 3, "bboxes": []}, 422, None, None),
        (None, 1, {"pose_id": 1, "bboxes": (0.6, 0.6, 0.6, 0.6, 0.6)}, 422, None, None),
        (None, 1, {"pose_id": 1, "bboxes": "[(0.6, 0.6, 0.6, 0.6, 0.6)]"}, 422, None, None),
        (None, 0, {"pose_id": 3, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 403, "Access forbidden.", None),
        (
            None,
            1,
            {"pose_id": 3, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"},
            201,
            None,
            0,
        ),
        # sequence creation
        (
            None,
            1,
            {"pose_id": 3, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"},
            201,
            None,
            2,
        ),
        # multiple bboxes produce multiple detections
        (
            None,
            1,
            {"pose_id": 3, "bboxes": "[(0.6,0.6,0.7,0.7,0.6),(0.2,0.2,0.3,0.3,0.8)]"},
            201,
            None,
            0,
        ),
    ],
)
@pytest.mark.asyncio
async def test_create_detection(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    mock_img: bytes,
    user_idx: Union[int, None],
    cam_idx: Union[int, None],
    payload: Dict[str, Any],
    status_code: int,
    status_detail: Union[str, None],
    repeat: Union[int, None],
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

    response = await async_client.post(
        "/detections", data=payload, files={"file": ("logo.png", mock_img, "image/png")}, headers=auth
    )
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        data = response.json()
        assert data["pose_id"] == payload.get("pose_id")
        if isinstance(payload.get("bboxes"), str):
            boxes = literal_eval(payload["bboxes"])
            if len(boxes) <= 1:
                assert data["bboxes"] == payload["bboxes"]
                assert data.get("others_bboxes") is None
            else:
                det_boxes = literal_eval(data["bboxes"])
                assert len(det_boxes) == 1
                assert det_boxes[0] in boxes
                assert data.get("others_bboxes") is not None
        assert data["id"] == max(entry["id"] for entry in pytest.detection_table) + 1
        assert data["camera_id"] == pytest.camera_table[cam_idx]["id"]
    created_ids: List[int] = []
    if response.status_code // 100 == 2:
        created_ids.append(response.json()["id"])
    if isinstance(repeat, int) and repeat > 0:
        det_ids = [response.json()["id"]]
        for _ in range(repeat):
            response = await async_client.post(
                "/detections", data=payload, files={"file": ("logo.png", mock_img, "image/png")}, headers=auth
            )
            assert response.status_code == status_code, print(response.__dict__)
            det_ids.append(response.json()["id"])
        # Final response will have a sequence_id
        assert isinstance(response.json()["sequence_id"], int)
        sequence_id = response.json()["sequence_id"]
        # Check that the other detections have the same sequence_id
        for det_id in det_ids[:-1]:
            response = await async_client.get(
                f"/detections/{det_id}",
                headers=pytest.get_token(
                    pytest.user_table[0]["id"],
                    pytest.user_table[0]["role"].split(),
                    pytest.user_table[0]["organization_id"],
                ),
            )
            assert response.status_code == 200
            assert response.json()["sequence_id"] == sequence_id
        created_ids.extend(det_ids)

    # Multi-bbox input should create one detection per bbox and store siblings in others_bboxes
    if response.status_code == 201 and isinstance(payload.get("bboxes"), str) and repeat in (0, None):
        boxes = literal_eval(payload["bboxes"])
        if len(boxes) <= 1:
            return
        bucket_key = response.json()["bucket_key"]
        latest_res = await detection_session.exec(
            select(Detection).where(Detection.bucket_key == bucket_key)  # type: ignore[attr-defined]
        )
        dets = latest_res.all()
        assert len(dets) == len(boxes)
        assert {det.pose_id for det in dets} == {payload["pose_id"]}
        assert {det.bucket_key for det in dets} == {bucket_key}
        box_counter = Counter(boxes)
        for det in dets:
            det_boxes = literal_eval(det.bboxes)
            assert len(det_boxes) == 1
            det_box = det_boxes[0]
            assert det_box in box_counter
            expected_others = []
            for box, count in box_counter.items():
                expected_others.extend([box] * count)
            expected_others.remove(det_box)
            assert det.others_bboxes is not None
            assert Counter(literal_eval(det.others_bboxes)) == Counter(expected_others)


def test_parse_bbox_invalid_syntax_raises():
    with pytest.raises(HTTPException) as exc:
        _parse_bbox("not-a-bbox")
    assert exc.value.status_code == 422


def test_parse_bbox_invalid_shape_raises():
    with pytest.raises(HTTPException) as exc:
        _parse_bbox("(0.1,0.2)")
    assert exc.value.status_code == 422


@pytest.mark.asyncio
async def test_create_detection_rejects_inverted_bbox(
    async_client: AsyncClient, detection_session: AsyncSession, mock_img: bytes
):
    auth = pytest.get_token(
        pytest.camera_table[0]["id"],
        ["camera"],
        pytest.camera_table[0]["organization_id"],
    )
    payload = {"pose_id": pytest.pose_table[0]["id"], "bboxes": "[(0.9,0.1,0.2,0.2,0.9)]"}
    response = await async_client.post(
        "/detections", data=payload, files={"file": ("logo.png", mock_img, "image/png")}, headers=auth
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "xmin & ymin are expected to be respectively smaller than xmax & ymax"


@pytest.mark.asyncio
async def test_create_detection_rejects_empty_bbox_strings(
    async_client: AsyncClient, detection_session: AsyncSession, mock_img: bytes, monkeypatch
):
    monkeypatch.setattr(detections_api, "_extract_bbox_strings", lambda _: [])
    auth = pytest.get_token(
        pytest.camera_table[0]["id"],
        ["camera"],
        pytest.camera_table[0]["organization_id"],
    )
    payload = {"pose_id": pytest.pose_table[0]["id"], "bboxes": "[(0.1,0.1,0.2,0.2,0.9)]"}
    response = await async_client.post(
        "/detections", data=payload, files={"file": ("logo.png", mock_img, "image/png")}, headers=auth
    )
    assert response.status_code == 422
    assert response.json()["detail"] == "Invalid bbox format."


@pytest.mark.asyncio
async def test_get_last_bbox_for_sequence_returns_latest(detection_session: AsyncSession):
    detections = DetectionCRUD(detection_session)
    now = datetime.utcnow()
    camera_id = pytest.camera_table[0]["id"]

    pose = Pose(camera_id=camera_id, azimuth=50.0)
    detection_session.add(pose)
    await detection_session.commit()
    await detection_session.refresh(pose)

    sequence = Sequence(
        camera_id=camera_id,
        pose_id=pose.id,
        camera_azimuth=50.0,
        sequence_azimuth=50.0,
        cone_angle=10.0,
        started_at=now - timedelta(seconds=10),
        last_seen_at=now,
    )
    detection_session.add(sequence)
    await detection_session.commit()
    await detection_session.refresh(sequence)

    det1 = Detection(
        camera_id=camera_id,
        pose_id=pose.id,
        sequence_id=sequence.id,
        bucket_key="bbox-1",
        bboxes="[(0.1,0.1,0.2,0.2,0.9)]",
        created_at=now - timedelta(seconds=5),
    )
    det2 = Detection(
        camera_id=camera_id,
        pose_id=pose.id,
        sequence_id=sequence.id,
        bucket_key="bbox-2",
        bboxes="[(0.3,0.3,0.4,0.4,0.9)]",
        created_at=now,
    )
    detection_session.add(det1)
    detection_session.add(det2)
    await detection_session.commit()

    last_bbox = await _get_last_bbox_for_sequence(detections, sequence.id)
    assert last_bbox == (0.3, 0.3, 0.4, 0.4, 0.9)


@pytest.mark.asyncio
async def test_get_last_bbox_for_sequence_returns_none_without_detections(detection_session: AsyncSession):
    detections = DetectionCRUD(detection_session)
    now = datetime.utcnow()
    camera_id = pytest.camera_table[0]["id"]
    pose = Pose(camera_id=camera_id, azimuth=60.0)
    detection_session.add(pose)
    await detection_session.commit()
    await detection_session.refresh(pose)

    sequence = Sequence(
        camera_id=camera_id,
        pose_id=pose.id,
        camera_azimuth=60.0,
        sequence_azimuth=60.0,
        cone_angle=10.0,
        started_at=now - timedelta(seconds=10),
        last_seen_at=now,
    )
    detection_session.add(sequence)
    await detection_session.commit()
    await detection_session.refresh(sequence)

    last_bbox = await _get_last_bbox_for_sequence(detections, sequence.id)
    assert last_bbox is None


@pytest.mark.asyncio
async def test_get_last_bbox_for_sequence_returns_none_for_invalid_bbox(detection_session: AsyncSession):
    detections = DetectionCRUD(detection_session)
    now = datetime.utcnow()
    camera_id = pytest.camera_table[0]["id"]
    pose = Pose(camera_id=camera_id, azimuth=70.0)
    detection_session.add(pose)
    await detection_session.commit()
    await detection_session.refresh(pose)

    sequence = Sequence(
        camera_id=camera_id,
        pose_id=pose.id,
        camera_azimuth=70.0,
        sequence_azimuth=70.0,
        cone_angle=10.0,
        started_at=now - timedelta(seconds=10),
        last_seen_at=now,
    )
    detection_session.add(sequence)
    await detection_session.commit()
    await detection_session.refresh(sequence)

    det = Detection(
        camera_id=camera_id,
        pose_id=pose.id,
        sequence_id=sequence.id,
        bucket_key="bbox-invalid",
        bboxes="[]",
        created_at=now,
    )
    detection_session.add(det)
    await detection_session.commit()

    last_bbox = await _get_last_bbox_for_sequence(detections, sequence.id)
    assert last_bbox is None


@pytest.mark.asyncio
async def test_get_camera_by_id_adds_missing_sequence_camera(detection_session: AsyncSession):
    cam_crud = CameraCRUD(detection_session)
    camera = await detection_session.get(Camera, pytest.camera_table[0]["id"])
    assert camera is not None

    missing_camera_id = 999
    camera_by_id = await _get_camera_by_id(camera, cam_crud, missing_camera_id)
    assert camera_by_id[missing_camera_id].id == camera.id


@pytest.mark.asyncio
async def test_get_recent_sequences_appends_missing_sequence(detection_session: AsyncSession):
    seq_crud = SequenceCRUD(detection_session)
    now = datetime.utcnow()
    camera_id = pytest.camera_table[0]["id"]
    pose_id = pytest.pose_table[0]["id"]
    old_seq = Sequence(
        camera_id=camera_id,
        pose_id=pose_id,
        camera_azimuth=12.0,
        sequence_azimuth=12.0,
        cone_angle=10.0,
        started_at=now - timedelta(seconds=120),
        last_seen_at=now - timedelta(seconds=settings.SEQUENCE_RELAXATION_SECONDS + 30),
    )
    recent_seq = Sequence(
        camera_id=camera_id,
        pose_id=pose_id,
        camera_azimuth=20.0,
        sequence_azimuth=20.0,
        cone_angle=10.0,
        started_at=now - timedelta(seconds=30),
        last_seen_at=now,
    )
    detection_session.add(old_seq)
    detection_session.add(recent_seq)
    await detection_session.commit()
    await detection_session.refresh(old_seq)

    recent_sequences = await _get_recent_sequences(seq_crud, [camera_id], old_seq)
    assert any(seq.id == old_seq.id for seq in recent_sequences)


@pytest.mark.asyncio
async def test_build_overlap_records_skips_missing_cone_data(detection_session: AsyncSession):
    now = datetime.utcnow()
    camera = await detection_session.get(Camera, pytest.camera_table[0]["id"])
    assert camera is not None
    seq = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=0.0,
        sequence_azimuth=None,
        cone_angle=None,
        started_at=now,
        last_seen_at=now,
    )
    records = _build_overlap_records([seq], {camera.id: camera})
    assert records == []


def test_resolve_groups_and_locations_empty_records_returns_none():
    assert _resolve_groups_and_locations([], 1) is None


def test_resolve_groups_and_locations_no_match_returns_none():
    now = datetime.utcnow()
    records = [
        {
            "id": 1,
            "lat": 3.6,
            "lon": -45.2,
            "sequence_azimuth": 10.0,
            "cone_angle": 20.0,
            "is_wildfire": None,
            "started_at": now - timedelta(seconds=10),
            "last_seen_at": now,
        }
    ]
    assert _resolve_groups_and_locations(records, 999) is None


@pytest.mark.asyncio
async def test_fetch_alert_mapping_empty(detection_session: AsyncSession):
    mapping = await _fetch_alert_mapping(detection_session, [])
    assert mapping == {}


@pytest.mark.asyncio
async def test_fetch_alert_mapping_returns_mapping(detection_session: AsyncSession):
    now = datetime.utcnow()
    alert = Alert(organization_id=1, lat=1.0, lon=1.0, started_at=now, last_seen_at=now)
    detection_session.add(alert)
    await detection_session.commit()
    await detection_session.refresh(alert)

    sequence = await detection_session.get(Sequence, pytest.sequence_table[0]["id"])
    assert sequence is not None
    link = AlertSequence(alert_id=alert.id, sequence_id=sequence.id)
    detection_session.add(link)
    await detection_session.commit()

    mapping = await _fetch_alert_mapping(detection_session, [sequence.id])
    assert mapping == {sequence.id: {alert.id}}


@pytest.mark.asyncio
async def test_maybe_update_alert_updates_fields(detection_session: AsyncSession):
    alert_crud = AlertCRUD(detection_session)
    now = datetime.utcnow()
    alert = Alert(organization_id=1, lat=None, lon=None, started_at=now, last_seen_at=now)
    detection_session.add(alert)
    await detection_session.commit()
    await detection_session.refresh(alert)

    location = (2.0, 3.0)
    start_at = now - timedelta(seconds=30)
    last_seen_at = now + timedelta(seconds=30)
    await _maybe_update_alert(alert_crud, alert.id, location, start_at, last_seen_at)

    updated = await alert_crud.get(alert.id, strict=True)
    assert updated.lat == location[0]
    assert updated.lon == location[1]
    assert updated.started_at == start_at
    assert updated.last_seen_at == last_seen_at


@pytest.mark.asyncio
async def test_get_or_create_alert_id_reuses_existing_alert(detection_session: AsyncSession):
    alert_crud = AlertCRUD(detection_session)
    now = datetime.utcnow()
    alert1 = Alert(organization_id=1, lat=None, lon=None, started_at=now, last_seen_at=now)
    alert2 = Alert(organization_id=1, lat=None, lon=None, started_at=now, last_seen_at=now)
    detection_session.add(alert1)
    detection_session.add(alert2)
    await detection_session.commit()
    await detection_session.refresh(alert1)
    await detection_session.refresh(alert2)

    location = (1.5, 2.5)
    target_id = await _get_or_create_alert_id(
        {alert2.id, alert1.id},
        location,
        1,
        now - timedelta(seconds=10),
        now + timedelta(seconds=10),
        alert_crud,
    )
    assert target_id == min(alert1.id, alert2.id)

    updated = await alert_crud.get(target_id, strict=True)
    assert updated.lat == location[0]
    assert updated.lon == location[1]


def test_build_links_for_group_skips_existing_alert():
    group = (1, 2, 3)
    mapping: Dict[int, set[int]] = {1: {10}, 2: set(), 3: {10}}
    links = _build_links_for_group(group, 10, mapping)
    assert {link.sequence_id for link in links} == {2}
    assert mapping[2] == {10}


@pytest.mark.asyncio
async def test_attach_sequence_to_alert_returns_without_overlap_records(detection_session: AsyncSession):
    seq_crud = SequenceCRUD(detection_session)
    alert_crud = AlertCRUD(detection_session)
    cam_crud = CameraCRUD(detection_session)
    camera = await detection_session.get(Camera, pytest.camera_table[0]["id"])
    assert camera is not None
    now = datetime.utcnow()
    sequence = Sequence(
        camera_id=camera.id,
        pose_id=None,
        camera_azimuth=0.0,
        sequence_azimuth=None,
        cone_angle=None,
        started_at=now,
        last_seen_at=now,
    )
    detection_session.add(sequence)
    await detection_session.commit()
    await detection_session.refresh(sequence)

    await _attach_sequence_to_alert(sequence, camera, cam_crud, seq_crud, alert_crud)

    alerts = await alert_crud.fetch_all()
    assert alerts == []


@pytest.mark.asyncio
async def test_detection_counts_split_sequences_and_alerts(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    mock_img: bytes,
    monkeypatch,
):
    monkeypatch.setattr(settings, "SEQUENCE_MIN_INTERVAL_DETS", 1)
    auth = pytest.get_token(
        pytest.camera_table[0]["id"],
        ["camera"],
        pytest.camera_table[0]["organization_id"],
    )
    pose_id = pytest.pose_table[0]["id"]

    bbox_a = "[(0.05,0.05,0.10,0.10,0.9)]"
    bbox_b = "[(0.90,0.90,0.95,0.95,0.9)]"
    bbox_both = "[(0.05,0.05,0.10,0.10,0.9),(0.90,0.90,0.95,0.95,0.9)]"

    async def count(model):
        res = await detection_session.exec(select(model))
        return len(res.all())

    base_det = await count(Detection)
    base_seq = await count(Sequence)
    base_alert = await count(Alert)
    base_map = await count(AlertSequence)

    resp1 = await async_client.post(
        "/detections",
        data={"pose_id": pose_id, "bboxes": bbox_a},
        files={"file": ("logo.png", mock_img, "image/png")},
        headers=auth,
    )
    assert resp1.status_code == 201, resp1.text
    assert await count(Detection) == base_det + 1
    assert await count(Sequence) == base_seq + 1
    assert await count(Alert) == base_alert + 1
    assert await count(AlertSequence) == base_map + 1

    resp2 = await async_client.post(
        "/detections",
        data={"pose_id": pose_id, "bboxes": bbox_a},
        files={"file": ("logo.png", mock_img, "image/png")},
        headers=auth,
    )
    assert resp2.status_code == 201, resp2.text
    assert await count(Detection) == base_det + 2
    assert await count(Sequence) == base_seq + 1
    assert await count(Alert) == base_alert + 1
    assert await count(AlertSequence) == base_map + 1

    resp3 = await async_client.post(
        "/detections",
        data={"pose_id": pose_id, "bboxes": bbox_b},
        files={"file": ("logo.png", mock_img, "image/png")},
        headers=auth,
    )
    assert resp3.status_code == 201, resp3.text
    assert await count(Detection) == base_det + 3
    assert await count(Sequence) == base_seq + 2
    assert await count(Alert) == base_alert + 2
    assert await count(AlertSequence) == base_map + 2

    resp4 = await async_client.post(
        "/detections",
        data={"pose_id": pose_id, "bboxes": bbox_both},
        files={"file": ("logo.png", mock_img, "image/png")},
        headers=auth,
    )
    assert resp4.status_code == 201, resp4.text
    assert await count(Detection) == base_det + 5
    assert await count(Sequence) == base_seq + 2
    assert await count(Alert) == base_alert + 2
    assert await count(AlertSequence) == base_map + 2


@pytest.mark.asyncio
async def test_create_detection_triggers_telegram_notifications(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    mock_img: bytes,
    monkeypatch,
):
    monkeypatch.setattr(settings, "SEQUENCE_MIN_INTERVAL_DETS", 1)
    calls: Dict[str, List[str]] = {"webhooks": [], "telegram": []}

    def fake_dispatch_webhook(url: str, det: Detection) -> None:
        calls["webhooks"].append(url)

    def fake_telegram_notify(channel_id: str, message: str) -> None:
        calls["telegram"].append(channel_id)

    monkeypatch.setattr(detections_api, "dispatch_webhook", fake_dispatch_webhook)
    monkeypatch.setattr(detections_api.telegram_client, "is_enabled", True)
    monkeypatch.setattr(detections_api.telegram_client, "notify", fake_telegram_notify)
    monkeypatch.setattr(detections_api.slack_client, "is_enabled", False)

    org = await detection_session.get(Organization, pytest.organization_table[0]["id"])
    assert org is not None
    org.telegram_id = "test-channel"
    detection_session.add(org)
    detection_session.add(Webhook(url="http://example.com/webhook-telegram"))
    await detection_session.commit()

    auth = pytest.get_token(
        pytest.camera_table[0]["id"],
        ["camera"],
        pytest.camera_table[0]["organization_id"],
    )
    payload = {"pose_id": pytest.pose_table[0]["id"], "bboxes": "[(0.1,0.1,0.2,0.2,0.9)]"}
    response = await async_client.post(
        "/detections", data=payload, files={"file": ("logo.png", mock_img, "image/png")}, headers=auth
    )
    assert response.status_code == 201, response.text
    assert calls["webhooks"]
    assert calls["telegram"] == ["test-channel"]


@pytest.mark.asyncio
async def test_create_detection_triggers_slack_notifications(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    mock_img: bytes,
    monkeypatch,
):
    monkeypatch.setattr(settings, "SEQUENCE_MIN_INTERVAL_DETS", 1)
    calls: Dict[str, List[str]] = {"webhooks": [], "slack": []}

    def fake_dispatch_webhook(url: str, det: Detection) -> None:
        calls["webhooks"].append(url)

    def fake_slack_notify(slack_hook: str, message: str, url: str, camera_name: str) -> object:
        calls["slack"].append(slack_hook)

        class DummyResponse:
            status_code = 200
            text = "ok"

        return DummyResponse()

    monkeypatch.setattr(detections_api, "dispatch_webhook", fake_dispatch_webhook)
    monkeypatch.setattr(detections_api.telegram_client, "is_enabled", False)
    monkeypatch.setattr(detections_api.slack_client, "is_enabled", True)
    monkeypatch.setattr(detections_api.slack_client, "notify", fake_slack_notify)

    org = await detection_session.get(Organization, pytest.organization_table[0]["id"])
    assert org is not None
    org.slack_hook = "http://example.com/slack"
    detection_session.add(org)
    detection_session.add(Webhook(url="http://example.com/webhook-slack"))
    await detection_session.commit()

    auth = pytest.get_token(
        pytest.camera_table[0]["id"],
        ["camera"],
        pytest.camera_table[0]["organization_id"],
    )
    payload = {"pose_id": pytest.pose_table[0]["id"], "bboxes": "[(0.12,0.12,0.2,0.2,0.9)]"}
    response = await async_client.post(
        "/detections", data=payload, files={"file": ("logo.png", mock_img, "image/png")}, headers=auth
    )
    assert response.status_code == 201, response.text
    assert calls["webhooks"]
    assert calls["slack"] == ["http://example.com/slack"]


@pytest.mark.asyncio
async def test_create_detection_sequence_flow_direct(detection_session: AsyncSession, monkeypatch):
    monkeypatch.setattr(settings, "SEQUENCE_MIN_INTERVAL_DETS", 1)
    monkeypatch.setattr(detections_api.telegram_client, "is_enabled", True)
    monkeypatch.setattr(detections_api.slack_client, "is_enabled", True)

    camera_id = pytest.camera_table[0]["id"]
    org_id = pytest.camera_table[0]["organization_id"]
    pose_id = pytest.pose_table[0]["id"]

    detections = DetectionCRUD(detection_session)
    webhooks = WebhookCRUD(detection_session)
    organizations = OrganizationCRUD(detection_session)
    sequences = SequenceCRUD(detection_session)
    alerts = AlertCRUD(detection_session)
    cameras = CameraCRUD(detection_session)
    poses = PoseCRUD(detection_session)
    org = await organizations.get(org_id, strict=True)
    org.telegram_id = "tg-channel"
    org.slack_hook = "http://example.com/slack-direct"
    detection_session.add(org)
    detection_session.add(Webhook(url="http://example.com/webhook-direct"))
    await detection_session.commit()

    invalid_det = Detection(
        camera_id=camera_id,
        pose_id=pose_id,
        sequence_id=None,
        bucket_key="invalid",
        bboxes="[]",
    )
    detection_session.add(invalid_det)
    await detection_session.commit()

    token_payload = TokenPayload(sub=camera_id, scopes=[Role.CAMERA], organization_id=org_id)
    upload = UploadFile(filename="img.png", file=io.BytesIO(b"img"))

    det_read = await create_detection(
        background_tasks=BackgroundTasks(),
        bboxes="[(0.2,0.2,0.3,0.3,0.9)]",
        pose_id=pose_id,
        file=upload,
        detections=detections,
        webhooks=webhooks,
        organizations=organizations,
        sequences=sequences,
        alerts=alerts,
        cameras=cameras,
        poses=poses,
        token_payload=token_payload,
    )
    assert det_read.sequence_id is not None

    created_sequences = await sequences.fetch_all(filters=[("camera_id", camera_id), ("pose_id", pose_id)])
    assert created_sequences
    actual_sequence = max(created_sequences, key=lambda seq: seq.id or 0)

    dummy_sequence = Sequence(
        camera_id=camera_id,
        pose_id=pose_id,
        camera_azimuth=actual_sequence.camera_azimuth,
        sequence_azimuth=actual_sequence.sequence_azimuth,
        cone_angle=actual_sequence.cone_angle,
        started_at=actual_sequence.started_at,
        last_seen_at=actual_sequence.last_seen_at,
    )

    async def fake_fetch_all(*args, **kwargs):
        await asyncio.sleep(0)
        return [dummy_sequence, actual_sequence]

    monkeypatch.setattr(sequences, "fetch_all", fake_fetch_all)

    upload_again = UploadFile(filename="img-2.png", file=io.BytesIO(b"img2"))
    det_read_2 = await create_detection(
        background_tasks=BackgroundTasks(),
        bboxes="[(0.25,0.25,0.35,0.35,0.9)]",
        pose_id=pose_id,
        file=upload_again,
        detections=detections,
        webhooks=webhooks,
        organizations=organizations,
        sequences=sequences,
        alerts=alerts,
        cameras=cameras,
        poses=poses,
        token_payload=token_payload,
    )
    assert det_read_2.sequence_id == actual_sequence.id


@pytest.mark.parametrize(
    ("user_idx", "detection_id", "status_code", "status_detail", "expected_idx"),
    [
        (None, 1, 401, "Not authenticated", None),
        (0, 0, 422, None, None),
        (0, 10, 404, "Table Detection has no corresponding entry.", None),
        (0, 1, 200, None, 0),
        (0, 2, 200, None, 1),
        (1, 1, 200, None, 0),
        (1, 2, 200, None, 1),
        (2, 1, 403, "Access forbidden.", None),
    ],
)
@pytest.mark.asyncio
async def test_get_detection(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    user_idx: Union[int, None],
    detection_id: int,
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

    response = await async_client.get(f"/detections/{detection_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == pytest.detection_table[expected_idx]


@pytest.mark.parametrize(
    ("user_idx", "status_code", "status_detail", "expected_result"),
    [
        (None, 401, "Not authenticated", None),
        (0, 200, None, pytest.detection_table),
        (1, 200, None, pytest.detection_table[:3]),
    ],
)
@pytest.mark.asyncio
async def test_fetch_detections(
    async_client: AsyncClient,
    detection_session: AsyncSession,
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

    response = await async_client.get("/detections", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() == expected_result


@pytest.mark.parametrize(
    ("user_idx", "detection_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 100, 404, "Table Detection has no corresponding entry."),
        (0, 1, 200, None),
        (1, 1, 200, None),
        (2, 1, 403, "Access forbidden."),
    ],
)
@pytest.mark.asyncio
async def test_get_detection_url(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    mock_img: bytes,
    user_idx: Union[int, None],
    detection_id: Union[int, None],
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

    response = await async_client.get(f"/detections/{detection_id}/url", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert isinstance(response.json()["url"], str)
        assert response.json()["url"].startswith("http://")


@pytest.mark.parametrize(
    ("user_idx", "detection_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (0, 0, 422, None),
        (0, 100, 404, "Table Detection has no corresponding entry."),
        (0, 1, 200, None),
        (0, 2, 200, None),
        (1, 1, 403, None),
        (1, 2, 403, None),
    ],
)
@pytest.mark.asyncio
async def test_delete_detection(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    user_idx: Union[int, None],
    detection_id: int,
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

    response = await async_client.delete(f"/detections/{detection_id}", headers=auth)
    assert response.status_code == status_code, print(response.__dict__)
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code // 100 == 2:
        assert response.json() is None


@pytest.mark.asyncio
async def test_create_detection_creates_sequence(
    async_client: AsyncClient, detection_session: AsyncSession, monkeypatch
):
    # Force sequence creation on first detection
    monkeypatch.setattr(settings, "SEQUENCE_MIN_INTERVAL_DETS", 1)
    mock_img = b"img"
    auth = pytest.get_token(pytest.camera_table[0]["id"], ["camera"], pytest.camera_table[0]["organization_id"])
    pose = Pose(camera_id=pytest.camera_table[0]["id"], azimuth=120.0)
    detection_session.add(pose)
    await detection_session.commit()
    await detection_session.refresh(pose)
    payload = {
        "pose_id": pose.id,
        "bboxes": "[(0.1,0.1,0.2,0.2,0.9)]",
    }
    resp = await async_client.post(
        "/detections", data=payload, files={"file": ("img.png", mock_img, "image/png")}, headers=auth
    )
    assert resp.status_code == 201, resp.text
    data = resp.json()
    assert data["sequence_id"] is not None

    seq_res = await detection_session.get(Sequence, data["sequence_id"])
    assert seq_res is not None
    assert seq_res.sequence_azimuth is not None
    assert seq_res.cone_angle is not None
    camera = await detection_session.get(Camera, pytest.camera_table[0]["id"])
    assert camera is not None
    expected_sequence_azimuth, expected_cone_angle = resolve_cone(
        float(pose.azimuth),
        str(payload["bboxes"]),
        camera.angle_of_view,
    )
    assert seq_res.sequence_azimuth == pytest.approx(expected_sequence_azimuth)
    assert seq_res.cone_angle == pytest.approx(expected_cone_angle)
    # Detection references the sequence
    det_res = await detection_session.get(Detection, data["id"])
    assert det_res is not None
    assert det_res.sequence_id == seq_res.id


@pytest.mark.asyncio
async def test_create_detection_creates_sequence_after_threshold(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    mock_img: bytes,
    monkeypatch,
):
    monkeypatch.setattr(settings, "SEQUENCE_MIN_INTERVAL_DETS", 2)
    auth = pytest.get_token(
        pytest.camera_table[0]["id"],
        ["camera"],
        pytest.camera_table[0]["organization_id"],
    )

    pose = Pose(camera_id=pytest.camera_table[0]["id"], azimuth=130.0)
    detection_session.add(pose)
    await detection_session.commit()
    await detection_session.refresh(pose)

    async def count_sequences() -> int:
        res = await detection_session.exec(select(Sequence))
        return len(res.all())

    base_seq = await count_sequences()

    resp1 = await async_client.post(
        "/detections",
        data={"pose_id": pose.id, "bboxes": "[(0.10,0.10,0.20,0.20,0.9)]"},
        files={"file": ("logo.png", mock_img, "image/png")},
        headers=auth,
    )
    assert resp1.status_code == 201, resp1.text
    det_id_1 = resp1.json()["id"]
    assert resp1.json()["sequence_id"] is None
    assert await count_sequences() == base_seq

    resp2 = await async_client.post(
        "/detections",
        data={"pose_id": pose.id, "bboxes": "[(0.12,0.12,0.22,0.22,0.9)]"},
        files={"file": ("logo.png", mock_img, "image/png")},
        headers=auth,
    )
    assert resp2.status_code == 201, resp2.text
    det_id_2 = resp2.json()["id"]
    seq_id = resp2.json()["sequence_id"]
    assert isinstance(seq_id, int)
    assert await count_sequences() == base_seq + 1

    det1_res = await detection_session.exec(
        select(Detection).where(Detection.id == det_id_1).execution_options(populate_existing=True)
    )
    det2_res = await detection_session.exec(
        select(Detection).where(Detection.id == det_id_2).execution_options(populate_existing=True)
    )
    det1 = det1_res.one()
    det2 = det2_res.one()
    assert det1.sequence_id == seq_id
    assert det2.sequence_id == seq_id


@pytest.mark.asyncio
async def test_attach_sequence_to_alert_creates_alert(detection_session: AsyncSession):
    seq_crud = SequenceCRUD(detection_session)
    alert_crud = AlertCRUD(detection_session)
    cam_crud = CameraCRUD(detection_session)
    now = datetime.utcnow()
    cam1 = await detection_session.get(Camera, 1)
    assert cam1 is not None
    cam2 = Camera(
        organization_id=1,
        name="cam-3",
        angle_of_view=90.0,
        elevation=100.0,
        lat=3.7,
        lon=-45.0,
        is_trustable=True,
        last_active_at=now,
        last_image=None,
        created_at=now,
    )
    detection_session.add(cam2)
    await detection_session.commit()
    await detection_session.refresh(cam2)

    seq1 = Sequence(
        camera_id=cam1.id,
        pose_id=None,
        camera_azimuth=0.0,
        sequence_azimuth=0.0,
        cone_angle=90.0,
        is_wildfire=None,
        started_at=now - timedelta(seconds=30),
        last_seen_at=now - timedelta(seconds=20),
    )
    seq2 = Sequence(
        camera_id=cam2.id,
        pose_id=None,
        camera_azimuth=5.0,
        sequence_azimuth=5.0,
        cone_angle=90.0,
        is_wildfire=None,
        started_at=now - timedelta(seconds=25),
        last_seen_at=now - timedelta(seconds=10),
    )
    detection_session.add(seq1)
    detection_session.add(seq2)
    await detection_session.commit()
    await detection_session.refresh(seq1)
    await detection_session.refresh(seq2)

    await _attach_sequence_to_alert(seq2, cam2, cam_crud, seq_crud, alert_crud)

    alerts = await alert_crud.fetch_all()
    assert len(alerts) == 1
    alert = alerts[0]
    assert alert.started_at == min(seq1.started_at, seq2.started_at)
    assert alert.last_seen_at == max(seq1.last_seen_at, seq2.last_seen_at)
    assert alert.lat is not None
    assert alert.lon is not None

    mappings_res = await detection_session.exec(select(AlertSequence))
    mappings = mappings_res.all()
    assert {(m.alert_id, m.sequence_id) for m in mappings} == {(alert.id, seq1.id), (alert.id, seq2.id)}
