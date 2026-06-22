# Copyright (C) 2025-2026, Pyronear.
#
# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import csv
import io
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple, cast

import pandas as pd
import pytest  # type: ignore
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints.alerts import _ALERT_EXPORT_COLUMNS, _iter_alerts_csv
from app.core.config import settings
from app.core.time import utcnow
from app.models import Alert, AlertSequence, AnnotationType, Camera, Detection, Organization, Pose, Sequence
from app.services.overlap import compute_overlap
from app.services.validation import process_next_due_validation


async def _create_alert_with_sequences(
    session: AsyncSession, org_id: int, camera_id: int, lat: float, lon: float
) -> Tuple[Alert, List[int], List[int]]:
    now = utcnow()
    pose = (
        await session.exec(select(Pose).where(Pose.camera_id == camera_id).order_by(Pose.id))  # type: ignore[attr-defined]
    ).first()
    assert pose is not None
    seq_payloads = [
        {
            "camera_id": camera_id,
            "pose_id": None,
            "camera_azimuth": 180.0,
            "is_wildfire": None,
            "sequence_azimuth": 163.4,
            "cone_angle": 1.0,
        },
        {
            "camera_id": camera_id,
            "pose_id": None,
            "camera_azimuth": 25.0,
            "is_wildfire": None,
            "sequence_azimuth": 8.3,
            "cone_angle": 0.8,
        },
        {
            "camera_id": camera_id,
            "pose_id": None,
            "camera_azimuth": 276.0,
            "is_wildfire": None,
            "sequence_azimuth": 276.5,
            "cone_angle": 3.0,
        },
    ]
    detections_count_by_sequence = [2, 1, 0]
    sequences: List[Sequence] = []
    for idx, payload in enumerate(seq_payloads):
        seq = Sequence(
            **payload,
            started_at=now - timedelta(seconds=10 * (idx + 1)),
            last_seen_at=now - timedelta(seconds=idx),
        )
        session.add(seq)
        sequences.append(seq)
    await session.commit()
    for seq in sequences:
        await session.refresh(seq)
    for sequence, detections_count in zip(sequences, detections_count_by_sequence, strict=True):
        for det_idx in range(detections_count):
            session.add(
                Detection(
                    camera_id=sequence.camera_id,
                    pose_id=pose.id,
                    sequence_id=sequence.id,
                    bucket_key=f"alert-seq-{sequence.id}-{det_idx}.jpg",
                    bbox="[(.1,.1,.7,.8,.9)]",
                    others_bboxes=None,
                    created_at=now - timedelta(seconds=det_idx),
                )
            )
    await session.commit()

    alert = Alert(
        organization_id=org_id,
        lat=lat,
        lon=lon,
        started_at=min(seq.started_at for seq in sequences),
        last_seen_at=max(seq.last_seen_at for seq in sequences),
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)

    for seq in sequences:
        session.add(AlertSequence(alert_id=alert.id, sequence_id=seq.id))
    await session.commit()
    return alert, [seq.id for seq in sequences], detections_count_by_sequence


@pytest.mark.asyncio
async def test_get_alert_and_sequences(async_client: AsyncClient, detection_session: AsyncSession):
    alert, seq_ids, detections_count_by_sequence = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )
    expected_counts = dict(zip(seq_ids, detections_count_by_sequence, strict=False))

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )

    resp = await async_client.get(f"/alerts/{alert.id}", headers=auth)
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert payload["id"] == alert.id
    assert payload["lat"] == pytest.approx(alert.lat)
    assert payload["lon"] == pytest.approx(alert.lon)
    assert payload["started_at"] == alert.started_at.isoformat()
    assert payload["last_seen_at"] == alert.last_seen_at.isoformat()
    assert {seq["id"] for seq in payload["sequences"]} == set(seq_ids)
    assert {seq["id"]: seq["detections_count"] for seq in payload["sequences"]} == expected_counts

    resp = await async_client.get(f"/alerts/{alert.id}/sequences?limit=5&desc=true", headers=auth)
    assert resp.status_code == 200, resp.text
    returned = resp.json()
    last_seen_times = [item["last_seen_at"] for item in returned]
    assert last_seen_times == sorted(last_seen_times, reverse=True)
    assert {sequence["id"]: sequence["detections_count"] for sequence in returned} == expected_counts
    assert any(sequence["detections_count"] == 0 for sequence in returned)


@pytest.mark.asyncio
async def test_alerts_unlabeled_latest(async_client: AsyncClient, detection_session: AsyncSession):
    alert, seq_ids, detections_count_by_sequence = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )
    expected_counts = dict(zip(seq_ids, detections_count_by_sequence, strict=False))

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get("/alerts/unlabeled/latest", headers=auth)
    assert resp.status_code == 200, resp.text
    payload = resp.json()
    assert any(item["id"] == alert.id for item in payload)
    returned = next(item for item in payload if item["id"] == alert.id)
    assert returned["lat"] == pytest.approx(alert.lat)
    assert returned["lon"] == pytest.approx(alert.lon)
    assert returned["started_at"] == alert.started_at.isoformat()
    assert returned["last_seen_at"] == alert.last_seen_at.isoformat()
    assert {seq["id"] for seq in returned["sequences"]} == set(seq_ids)
    assert {seq["id"]: seq["detections_count"] for seq in returned["sequences"]} == expected_counts
    assert any(seq["detections_count"] == 0 for seq in returned["sequences"])


@pytest.mark.asyncio
async def test_alerts_unlabeled_latest_pagination(async_client: AsyncClient, detection_session: AsyncSession):
    alert_a, _, _ = await _create_alert_with_sequences(detection_session, org_id=1, camera_id=1, lat=48.0, lon=2.0)
    alert_b, _, _ = await _create_alert_with_sequences(detection_session, org_id=1, camera_id=1, lat=48.1, lon=2.1)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )

    resp = await async_client.get("/alerts/unlabeled/latest?limit=10&offset=0", headers=auth)
    assert resp.status_code == 200, resp.text
    full = resp.json()
    full_ids = [item["id"] for item in full]
    assert {alert_a.id, alert_b.id}.issubset(full_ids)

    resp = await async_client.get("/alerts/unlabeled/latest?limit=1&offset=0", headers=auth)
    assert resp.status_code == 200, resp.text
    page_one = resp.json()
    assert len(page_one) == 1
    assert page_one[0]["id"] == full_ids[0]

    resp = await async_client.get("/alerts/unlabeled/latest?limit=1&offset=1", headers=auth)
    assert resp.status_code == 200, resp.text
    page_two = resp.json()
    assert len(page_two) == 1
    assert page_two[0]["id"] == full_ids[1]


@pytest.mark.asyncio
async def test_alerts_from_date(async_client: AsyncClient, detection_session: AsyncSession):
    alert, seq_ids, detections_count_by_sequence = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )
    expected_counts = dict(zip(seq_ids, detections_count_by_sequence, strict=False))
    date_str = alert.started_at.date().isoformat()

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(f"/alerts/all/fromdate?from_date={date_str}", headers=auth)
    assert resp.status_code == 200, resp.text
    assert any(item["id"] == alert.id for item in resp.json())

    # Ensure order is by started_at desc
    returned = resp.json()
    started_times = [item["started_at"] for item in returned]
    assert started_times == sorted(started_times, reverse=True)
    alert_payload = next(item for item in returned if item["id"] == alert.id)
    assert {seq["id"] for seq in alert_payload["sequences"]} == set(seq_ids)
    assert {seq["id"]: seq["detections_count"] for seq in alert_payload["sequences"]} == expected_counts
    assert any(seq["detections_count"] == 0 for seq in alert_payload["sequences"])


@pytest.mark.asyncio
async def test_triangulation_creates_single_alert(
    async_client: AsyncClient, detection_session: AsyncSession, mock_img: bytes
):
    organization = await detection_session.get(Organization, 1)
    assert organization is not None
    organization.name = "sdis-77"
    detection_session.add(organization)
    await detection_session.commit()
    await detection_session.refresh(organization)

    camera_specs = [
        {
            "name": "croix-augas",
            "lat": 48.4267,
            "lon": 2.7109,
            "azimuth": 190.0,
            "bboxes": "[(0,0.530,0.018,0.553,0.183)]",
        },
        {
            "name": "nemours",
            "lat": 48.2605,
            "lon": 2.7064,
            "azimuth": 25.0,
            "bboxes": "[(0.184,0.425,0.199,0.447,0.557)]",
        },
        {
            "name": "moret-sur-loing",
            "lat": 48.3792,
            "lon": 2.8208,
            "azimuth": 280.0,
            "bboxes": "[(0.408,0.462,0.463,0.496,0.498)]",
        },
    ]
    cameras: List[Camera] = []
    for spec in camera_specs:
        camera = Camera(
            organization_id=organization.id,
            name=spec["name"],
            angle_of_view=54.2,
            elevation=110.0,
            lat=spec["lat"],
            lon=spec["lon"],
            is_trustable=True,
        )
        detection_session.add(camera)
        cameras.append(camera)
    await detection_session.commit()
    for camera in cameras:
        await detection_session.refresh(camera)

    poses: List[Pose] = []
    for camera, spec in zip(cameras, camera_specs, strict=False):
        pose = Pose(camera_id=camera.id, azimuth=spec["azimuth"])
        detection_session.add(pose)
        poses.append(pose)
    await detection_session.commit()
    for pose in poses:
        await detection_session.refresh(pose)

    for _ in range(settings.SEQUENCE_MIN_INTERVAL_DETS):
        for camera, spec, pose in zip(cameras, camera_specs, poses, strict=False):
            auth = pytest.get_token(camera.id, ["camera"], organization.id)
            response = await async_client.post(
                "/detections",
                data={"pose_id": pose.id, "bboxes": spec["bboxes"]},
                files={"file": ("logo.png", mock_img, "image/png")},
                headers=auth,
            )
            assert response.status_code == 201, response.text

    # The worker loop is not running in tests: drain the due sequences synchronously
    # (temporal unconfigured -> fail-open validates, then triangulation runs).
    while await process_next_due_validation():
        pass

    camera_ids = [camera.id for camera in cameras]
    seqs_res = await detection_session.exec(
        select(Sequence).where(cast(Any, Sequence.camera_id).in_(camera_ids)).execution_options(populate_existing=True)
    )
    sequences = sorted(seqs_res.all(), key=lambda seq: seq.id)
    assert len(sequences) == len(cameras)

    seq_ids = {seq.id for seq in sequences}
    mappings_res = await detection_session.exec(
        select(AlertSequence.alert_id, AlertSequence.sequence_id).where(
            cast(Any, AlertSequence.sequence_id).in_(list(seq_ids))
        )
    )
    mappings = set(mappings_res.all())
    alert_ids = {aid for aid, _ in mappings}
    assert len(alert_ids) == 1
    assert {sid for _, sid in mappings} == seq_ids

    alert_res = await detection_session.exec(select(Alert).where(Alert.id == next(iter(alert_ids))))
    alert = alert_res.one()
    assert alert.organization_id == organization.id

    camera_by_id = {camera.id: camera for camera in cameras}
    records = [
        {
            "id": seq.id,
            "pose_id": seq.pose_id,
            "lat": camera_by_id[seq.camera_id].lat,
            "lon": camera_by_id[seq.camera_id].lon,
            "sequence_azimuth": seq.sequence_azimuth,
            "cone_angle": seq.cone_angle,
            "is_wildfire": seq.is_wildfire,
            "started_at": seq.started_at,
            "last_seen_at": seq.last_seen_at,
        }
        for seq in sequences
    ]
    df = compute_overlap(pd.DataFrame.from_records(records))
    expected_loc = None
    for groups, locations in zip(df["event_groups"], df["event_smoke_locations"], strict=False):
        for idx, group in enumerate(groups):
            if set(group) == seq_ids:
                if idx < len(locations):
                    expected_loc = locations[idx]
                break
        if expected_loc is not None:
            break

    assert expected_loc is not None
    assert alert.lat == pytest.approx(expected_loc[0])
    assert alert.lon == pytest.approx(expected_loc[1])

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    initial_alert_id = next(iter(alert_ids))
    initial_mappings = set(mappings)

    resp = await async_client.patch(
        f"/sequences/{sequences[0].id}/label",
        json={"is_wildfire": AnnotationType.WILDFIRE_SMOKE.value},
        headers=auth,
    )
    assert resp.status_code == 200, resp.text

    mappings_res = await detection_session.exec(
        select(AlertSequence.alert_id, AlertSequence.sequence_id).where(
            cast(Any, AlertSequence.sequence_id).in_(list(seq_ids))
        )
    )
    mappings_after_wildfire = set(mappings_res.all())
    alert_ids_after_wildfire = {aid for aid, _ in mappings_after_wildfire}
    assert alert_ids_after_wildfire == {initial_alert_id}
    assert mappings_after_wildfire == initial_mappings

    resp = await async_client.patch(
        f"/sequences/{sequences[1].id}/label",
        json={"is_wildfire": AnnotationType.OTHER_SMOKE.value},
        headers=auth,
    )
    assert resp.status_code == 200, resp.text

    mappings_res = await detection_session.exec(
        select(AlertSequence.alert_id, AlertSequence.sequence_id).where(
            cast(Any, AlertSequence.sequence_id).in_(list(seq_ids))
        )
    )
    mappings_after_other = set(mappings_res.all())
    alert_ids_after_other = {aid for aid, _ in mappings_after_other}
    assert len(alert_ids_after_other) == 2
    new_alert_ids = alert_ids_after_other - {initial_alert_id}
    assert len(new_alert_ids) == 1
    new_alert_id = next(iter(new_alert_ids))

    assert {sid for aid, sid in mappings_after_other if aid == new_alert_id} == {sequences[1].id}
    remaining_ids = {seq.id for seq in sequences if seq.id != sequences[1].id}
    updated_mappings = {(aid, sid) for aid, sid in mappings_after_other if aid == initial_alert_id}
    assert updated_mappings == {(initial_alert_id, sid) for sid in remaining_ids}


@pytest.mark.asyncio
async def test_unmatch_creates_new_alert(async_client: AsyncClient, detection_session: AsyncSession):
    alert, seq_ids, _ = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )
    target_seq = seq_ids[0]
    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )

    resp = await async_client.post(f"/alerts/{alert.id}/sequences/{target_seq}/unmatch", headers=auth)
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body is not None
    assert body["id"] != alert.id
    assert body["organization_id"] == alert.organization_id
    assert body["lat"] is None
    assert body["lon"] is None
    assert {seq["id"] for seq in body["sequences"]} == {target_seq}

    mappings_res = await detection_session.exec(
        select(AlertSequence.alert_id, AlertSequence.sequence_id).where(
            cast(Any, AlertSequence.sequence_id).in_(seq_ids)
        )
    )
    mappings = set(mappings_res.all())
    assert (alert.id, target_seq) not in mappings
    assert (body["id"], target_seq) in mappings
    remaining_for_original = {sid for aid, sid in mappings if aid == alert.id}
    assert remaining_for_original == set(seq_ids[1:])


@pytest.mark.asyncio
async def test_unmatch_keeps_sequence_when_already_linked_elsewhere(
    async_client: AsyncClient, detection_session: AsyncSession
):
    alert, seq_ids, _ = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )
    target_seq = seq_ids[0]

    other_alert = Alert(
        organization_id=alert.organization_id,
        lat=None,
        lon=None,
        started_at=alert.started_at,
        last_seen_at=alert.last_seen_at,
    )
    detection_session.add(other_alert)
    await detection_session.commit()
    await detection_session.refresh(other_alert)
    detection_session.add(AlertSequence(alert_id=other_alert.id, sequence_id=target_seq))
    await detection_session.commit()

    auth = pytest.get_token(
        pytest.user_table[1]["id"], pytest.user_table[1]["role"].split(), pytest.user_table[1]["organization_id"]
    )
    resp = await async_client.post(f"/alerts/{alert.id}/sequences/{target_seq}/unmatch", headers=auth)
    assert resp.status_code == 200, resp.text
    assert resp.json() is None

    mappings_res = await detection_session.exec(
        select(AlertSequence.alert_id, AlertSequence.sequence_id).where(AlertSequence.sequence_id == target_seq)
    )
    alert_ids_for_seq = {aid for aid, _ in mappings_res.all()}
    assert alert_ids_for_seq == {other_alert.id}


@pytest.mark.asyncio
async def test_unmatch_rejects_single_sequence_alert(async_client: AsyncClient, detection_session: AsyncSession):
    now = utcnow()
    seq = Sequence(
        camera_id=1,
        pose_id=None,
        camera_azimuth=10.0,
        is_wildfire=None,
        sequence_azimuth=10.0,
        cone_angle=1.0,
        started_at=now - timedelta(seconds=30),
        last_seen_at=now,
    )
    detection_session.add(seq)
    await detection_session.commit()
    await detection_session.refresh(seq)

    alert = Alert(
        organization_id=1,
        lat=None,
        lon=None,
        started_at=seq.started_at,
        last_seen_at=seq.last_seen_at,
    )
    detection_session.add(alert)
    await detection_session.commit()
    await detection_session.refresh(alert)
    detection_session.add(AlertSequence(alert_id=alert.id, sequence_id=seq.id))
    await detection_session.commit()

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.post(f"/alerts/{alert.id}/sequences/{seq.id}/unmatch", headers=auth)
    assert resp.status_code == 400, resp.text


@pytest.mark.asyncio
async def test_unmatch_returns_404_when_sequence_not_linked(async_client: AsyncClient, detection_session: AsyncSession):
    alert, _, _ = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )
    other_seq = Sequence(
        camera_id=1,
        pose_id=None,
        camera_azimuth=10.0,
        is_wildfire=None,
        sequence_azimuth=10.0,
        cone_angle=1.0,
        started_at=utcnow() - timedelta(seconds=30),
        last_seen_at=utcnow(),
    )
    detection_session.add(other_seq)
    await detection_session.commit()
    await detection_session.refresh(other_seq)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.post(f"/alerts/{alert.id}/sequences/{other_seq.id}/unmatch", headers=auth)
    assert resp.status_code == 404, resp.text


@pytest.mark.asyncio
async def test_unmatch_forbidden_for_user_role(async_client: AsyncClient, detection_session: AsyncSession):
    alert, seq_ids, _ = await _create_alert_with_sequences(
        detection_session, org_id=2, camera_id=2, lat=48.3856355, lon=2.7323256
    )
    auth = pytest.get_token(
        pytest.user_table[2]["id"], pytest.user_table[2]["role"].split(), pytest.user_table[2]["organization_id"]
    )
    resp = await async_client.post(f"/alerts/{alert.id}/sequences/{seq_ids[0]}/unmatch", headers=auth)
    assert resp.status_code == 403, resp.text


@pytest.mark.asyncio
async def test_unmatch_forbidden_cross_org(async_client: AsyncClient, detection_session: AsyncSession):
    other_alert, other_seq_ids, _ = await _create_alert_with_sequences(
        detection_session, org_id=2, camera_id=2, lat=48.3856355, lon=2.7323256
    )
    auth = pytest.get_token(
        pytest.user_table[1]["id"], pytest.user_table[1]["role"].split(), pytest.user_table[1]["organization_id"]
    )
    resp = await async_client.post(f"/alerts/{other_alert.id}/sequences/{other_seq_ids[0]}/unmatch", headers=auth)
    assert resp.status_code == 403, resp.text


async def _create_alert(
    session: AsyncSession,
    org_id: int,
    started_at: datetime,
    last_seen_at: datetime,
    lat: float | None = 48.0,
    lon: float | None = 2.0,
) -> Alert:
    alert = Alert(
        organization_id=org_id,
        lat=lat,
        lon=lon,
        started_at=started_at,
        last_seen_at=last_seen_at,
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    return alert


async def _attach_sequence(
    session: AsyncSession,
    alert: Alert,
    *,
    camera_id: int = 1,
    is_wildfire: AnnotationType | None = None,
    sequence_azimuth: float | None = 100.0,
    pose_id: int | None = None,
    started_at: datetime | None = None,
    last_seen_at: datetime | None = None,
) -> Sequence:
    seq = Sequence(
        camera_id=camera_id,
        pose_id=pose_id,
        camera_azimuth=100.0,
        is_wildfire=is_wildfire,
        sequence_azimuth=sequence_azimuth,
        cone_angle=1.0,
        started_at=started_at or alert.started_at,
        last_seen_at=last_seen_at or alert.last_seen_at,
    )
    session.add(seq)
    await session.commit()
    await session.refresh(seq)
    session.add(AlertSequence(alert_id=alert.id, sequence_id=seq.id))
    await session.commit()
    return seq


def _parse_export_csv(body: str) -> Tuple[List[str], List[Dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(body))
    rows = list(reader)
    return list(reader.fieldnames or []), rows


# ─────────────────────────────────────────────────────────────────────────────
# Unit tests for _iter_alerts_csv: pure serializer behavior, no DB / HTTP / auth
# ─────────────────────────────────────────────────────────────────────────────


_UNIT_BASE_DT = datetime(2026, 4, 10, 12, 0, 0)


def _make_alert(
    *,
    id_: int = 1,
    organization_id: int = 1,
    lat: float | None = 48.0,
    lon: float | None = 2.0,
    started_at: datetime | None = None,
    last_seen_at: datetime | None = None,
) -> Alert:
    return Alert(
        id=id_,
        organization_id=organization_id,
        lat=lat,
        lon=lon,
        started_at=started_at or _UNIT_BASE_DT,
        last_seen_at=last_seen_at or _UNIT_BASE_DT + timedelta(minutes=5),
    )


def _make_sequence(
    *,
    id_: int = 1,
    camera_id: int = 1,
    pose_id: int | None = None,
    is_wildfire: AnnotationType | None = None,
    sequence_azimuth: float | None = 100.0,
    started_at: datetime | None = None,
    last_seen_at: datetime | None = None,
) -> Sequence:
    return Sequence(
        id=id_,
        camera_id=camera_id,
        pose_id=pose_id,
        camera_azimuth=100.0,
        is_wildfire=is_wildfire,
        sequence_azimuth=sequence_azimuth,
        cone_angle=1.0,
        started_at=started_at or _UNIT_BASE_DT,
        last_seen_at=last_seen_at or _UNIT_BASE_DT + timedelta(minutes=5),
    )


def _run_iter(
    alerts: List[Alert],
    seq_map: Dict[int, List[Sequence]],
    camera_names_by_id: Dict[int, str],
) -> Tuple[List[str], List[Dict[str, str]]]:
    body = "".join(_iter_alerts_csv(alerts, seq_map, camera_names_by_id))
    return _parse_export_csv(body)


def test_iter_alerts_csv_emits_only_header_when_no_alerts():
    header, rows = _run_iter([], {}, {})
    assert header == _ALERT_EXPORT_COLUMNS
    assert rows == []


def test_iter_alerts_csv_renders_null_coordinates_as_empty():
    alert = _make_alert(lat=None, lon=None)
    sequence = _make_sequence()
    _, rows = _run_iter([alert], {alert.id: [sequence]}, {sequence.camera_id: "cam-1"})
    assert rows[0]["alert_triangulated_lat"] == ""
    assert rows[0]["alert_triangulated_lon"] == ""


def test_iter_alerts_csv_emits_one_row_per_sequence_sorted_by_started_at():
    alert = _make_alert(id_=10, started_at=_UNIT_BASE_DT, last_seen_at=_UNIT_BASE_DT + timedelta(minutes=30))
    # Provided in non-monotonic order to verify the serializer sorts ASC by sequence.started_at.
    sequences = [
        _make_sequence(
            id_=20,
            started_at=_UNIT_BASE_DT + timedelta(minutes=10),
            last_seen_at=_UNIT_BASE_DT + timedelta(minutes=20),
        ),
        _make_sequence(
            id_=30,
            started_at=_UNIT_BASE_DT + timedelta(minutes=20),
            last_seen_at=_UNIT_BASE_DT + timedelta(minutes=30),
        ),
        _make_sequence(id_=10, started_at=_UNIT_BASE_DT, last_seen_at=_UNIT_BASE_DT + timedelta(minutes=10)),
    ]
    _, rows = _run_iter([alert], {alert.id: sequences}, {1: "cam-1"})
    assert [int(r["sequence_id"]) for r in rows] == [10, 20, 30]
    # Alert-level cells repeat across rows
    assert {r["alert_started_at_date"] for r in rows} == {alert.started_at.date().isoformat()}
    assert {r["alert_last_seen_at"] for r in rows} == {alert.last_seen_at.isoformat()}


@pytest.mark.parametrize(
    ("is_wildfire", "expected_label"),
    [
        (AnnotationType.WILDFIRE_SMOKE, "wildfire"),
        (AnnotationType.OTHER_SMOKE, "other"),
        (AnnotationType.OTHER, "other"),
        (None, "unknown"),
    ],
)
def test_iter_alerts_csv_wildfire_label_mapping(is_wildfire: AnnotationType | None, expected_label: str):
    alert = _make_alert()
    sequence = _make_sequence(is_wildfire=is_wildfire)
    _, rows = _run_iter([alert], {alert.id: [sequence]}, {sequence.camera_id: "cam-1"})
    assert rows[0]["sequence_label"] == expected_label


def test_iter_alerts_csv_resolves_camera_name_per_sequence():
    alert = _make_alert()
    seq_a = _make_sequence(id_=1, camera_id=1, started_at=_UNIT_BASE_DT)
    seq_b = _make_sequence(id_=2, camera_id=99, started_at=_UNIT_BASE_DT + timedelta(minutes=10))
    _, rows = _run_iter([alert], {alert.id: [seq_a, seq_b]}, {1: "cam-a", 99: "cam-b"})
    cam_by_seq = {int(r["sequence_id"]): r["camera_name"] for r in rows}
    assert cam_by_seq == {1: "cam-a", 2: "cam-b"}


# ─────────────────────────────────────────────────────────────────────────────
# Integration tests for GET /alerts/export: route wiring, SQL filter, JWT scope
# ─────────────────────────────────────────────────────────────────────────────


async def _get_export(
    async_client: AsyncClient, auth: Dict[str, str], from_date: str, to_date: str
) -> Tuple[List[str], List[Dict[str, str]]]:
    resp = await async_client.get(f"/alerts/export?from_date={from_date}&to_date={to_date}", headers=auth)
    assert resp.status_code == 200, resp.text
    return _parse_export_csv(resp.text)


@pytest.fixture
def export_base_dt() -> datetime:
    """Anchor datetime for export integration tests; date is stable so query windows stay readable."""
    return datetime(2026, 4, 10, 12, 0, 0)


@pytest.fixture
def org1_admin_auth() -> Dict[str, str]:
    user = pytest.user_table[0]
    return pytest.get_token(user["id"], user["role"].split(), user["organization_id"])


@pytest.fixture
def org1_agent_auth() -> Dict[str, str]:
    user = pytest.user_table[1]
    return pytest.get_token(user["id"], user["role"].split(), user["organization_id"])


@pytest.mark.asyncio
async def test_alerts_export_happy_path(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    export_base_dt: datetime,
    org1_admin_auth: Dict[str, str],
):
    alerts: List[Alert] = []
    for offset_days, (lat, lon) in enumerate([(48.1, 2.1), (48.2, 2.2), (48.3, 2.3)]):
        started = export_base_dt + timedelta(days=offset_days)
        alert = await _create_alert(detection_session, 1, started, started + timedelta(minutes=5), lat, lon)
        await _attach_sequence(detection_session, alert)
        alerts.append(alert)

    resp = await async_client.get("/alerts/export?from_date=2026-04-10&to_date=2026-04-12", headers=org1_admin_auth)
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/csv")
    assert "attachment" in resp.headers["content-disposition"]
    assert "alerts_2026-04-10_2026-04-12.csv" in resp.headers["content-disposition"]

    _, rows = _parse_export_csv(resp.text)
    assert [int(r["alert_id"]) for r in rows] == [a.id for a in alerts]
    # ordering is ascending by alert.started_at
    started_iso = [f"{r['alert_started_at_date']}T{r['alert_started_at_time']}" for r in rows]
    assert started_iso == sorted(started_iso)
    # One dict equality covers column set, names, and values in a single pytest diff.
    first = rows[0]
    assert first == {
        "alert_id": str(alerts[0].id),
        "alert_started_at_date": alerts[0].started_at.date().isoformat(),
        "alert_started_at_time": alerts[0].started_at.time().isoformat(),
        "alert_last_seen_at": alerts[0].last_seen_at.isoformat(),
        "alert_duration_seconds": str(int((alerts[0].last_seen_at - alerts[0].started_at).total_seconds())),
        "alert_triangulated_lat": "48.1",
        "alert_triangulated_lon": "2.1",
        "organization_id": "1",
        "sequence_id": str(first["sequence_id"]),  # id auto-generated, just round-trip
        "sequence_started_at": alerts[0].started_at.isoformat(),
        "sequence_last_seen_at": alerts[0].last_seen_at.isoformat(),
        "sequence_triangulated_azimuth": "100.0",
        "sequence_label": "unknown",
        "pose_id": "",
        "camera_id": "1",
        "camera_name": "cam-1",
    }


@pytest.mark.asyncio
async def test_alerts_export_window_narrows(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    export_base_dt: datetime,
    org1_admin_auth: Dict[str, str],
):
    for offset_days in range(3):
        started = export_base_dt + timedelta(days=offset_days)
        alert = await _create_alert(detection_session, 1, started, started + timedelta(minutes=5))
        await _attach_sequence(detection_session, alert)

    _, rows = await _get_export(async_client, org1_admin_auth, "2026-04-11", "2026-04-11")
    returned_dates = {r["alert_started_at_date"] for r in rows}
    assert returned_dates == {"2026-04-11"}


@pytest.mark.asyncio
async def test_alerts_export_org_isolation(
    async_client: AsyncClient,
    detection_session: AsyncSession,
    export_base_dt: datetime,
    org1_agent_auth: Dict[str, str],
):
    org1_alert = await _create_alert(detection_session, 1, export_base_dt, export_base_dt + timedelta(minutes=5))
    await _attach_sequence(detection_session, org1_alert, camera_id=1)
    org2_alert = await _create_alert(detection_session, 2, export_base_dt, export_base_dt + timedelta(minutes=5))
    await _attach_sequence(detection_session, org2_alert, camera_id=2)

    _, rows = await _get_export(async_client, org1_agent_auth, "2026-04-10", "2026-04-10")
    returned_ids = {int(r["alert_id"]) for r in rows}
    assert org1_alert.id in returned_ids
    assert org2_alert.id not in returned_ids


@pytest.mark.asyncio
async def test_alerts_export_invalid_range(
    async_client: AsyncClient, detection_session: AsyncSession, org1_admin_auth: Dict[str, str]
):
    resp = await async_client.get("/alerts/export?from_date=2026-04-12&to_date=2026-04-10", headers=org1_admin_auth)
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_alerts_export_unauthenticated(async_client: AsyncClient, detection_session: AsyncSession):
    resp = await async_client.get("/alerts/export?from_date=2026-04-10&to_date=2026-04-12")
    assert resp.status_code == 401, resp.text
