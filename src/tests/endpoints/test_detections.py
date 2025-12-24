from datetime import datetime, timedelta
from typing import Any, Dict, List, Union

import pytest  # type: ignore
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints.detections import _attach_sequence_to_alert
from app.core.config import settings
from app.crud import AlertCRUD, CameraCRUD, SequenceCRUD
from app.models import AlertSequence, Camera, Detection, Sequence
from app.services.cones import resolve_cone


@pytest.mark.parametrize(
    ("user_idx", "cam_idx", "payload", "status_code", "status_detail", "repeat"),
    [
        (None, None, {"azimuth": 45.6, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 401, "Not authenticated", None),
        (0, None, {"azimuth": 45.6, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 403, "Incompatible token scope.", None),
        (1, None, {"azimuth": 45.6, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 403, "Incompatible token scope.", None),
        (2, None, {"azimuth": 45.6, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 403, "Incompatible token scope.", None),
        (None, 0, {"azimuth": "hello"}, 422, None, None),
        (None, 0, {}, 422, None, None),
        (None, 0, {"azimuth": 45.6, "bboxes": []}, 422, None, None),
        (None, 1, {"azimuth": 45.6, "bboxes": (0.6, 0.6, 0.6, 0.6, 0.6)}, 422, None, None),
        (None, 1, {"azimuth": 45.6, "bboxes": "[(0.6, 0.6, 0.6, 0.6, 0.6)]"}, 422, None, None),
        (None, 1, {"azimuth": 360, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]"}, 422, None, None),
        (
            None,
            1,
            {"azimuth": 45.6, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]", "pose_id": 3, "sequence_id": None},
            201,
            None,
            0,
        ),
        (
            None,
            1,
            {"azimuth": 0, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]", "pose_id": 3, "sequence_id": None},
            201,
            None,
            0,
        ),
        # sequence creation
        (
            None,
            1,
            {"azimuth": 45.6, "bboxes": "[(0.6,0.6,0.7,0.7,0.6)]", "pose_id": 3, "sequence_id": None},
            201,
            None,
            2,
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
        assert {
            k: v
            for k, v in response.json().items()
            if k not in {"created_at", "updated_at", "id", "bucket_key", "camera_id"}
        } == payload
        assert response.json()["id"] == max(entry["id"] for entry in pytest.detection_table) + 1
        assert response.json()["camera_id"] == pytest.camera_table[cam_idx]["id"]
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
    payload = {
        "azimuth": 120.0,
        "pose_id": None,
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
    assert seq_res.cone_azimuth is not None
    assert seq_res.cone_angle is not None
    camera = await detection_session.get(Camera, pytest.camera_table[0]["id"])
    assert camera is not None
    expected_cone_azimuth, expected_cone_angle = resolve_cone(
        float(payload["azimuth"] if payload["azimuth"] is not None else 0.0),
        str(payload["bboxes"]),
        camera.angle_of_view,
    )
    assert seq_res.cone_azimuth == pytest.approx(expected_cone_azimuth)
    assert seq_res.cone_angle == pytest.approx(expected_cone_angle)
    # Detection references the sequence
    det_res = await detection_session.get(Detection, data["id"])
    assert det_res is not None
    assert det_res.sequence_id == seq_res.id


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
        azimuth=0.0,
        cone_azimuth=0.0,
        cone_angle=90.0,
        is_wildfire=None,
        started_at=now - timedelta(seconds=30),
        last_seen_at=now - timedelta(seconds=20),
    )
    seq2 = Sequence(
        camera_id=cam2.id,
        pose_id=None,
        azimuth=5.0,
        cone_azimuth=5.0,
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
