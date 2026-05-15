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

from app.core.config import settings
from app.core.time import utcnow
from app.models import Alert, AlertSequence, AnnotationType, Camera, Detection, Organization, Pose, Sequence
from app.services.overlap import compute_overlap


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


_EXPORT_COLUMNS = [
    "alert_id",
    "alert_started_at_date",
    "alert_started_at_time",
    "alert_last_seen_at",
    "alert_duration_seconds",
    "alert_triangulated_lat",
    "alert_triangulated_lon",
    "organization_id",
    "sequence_id",
    "sequence_started_at",
    "sequence_last_seen_at",
    "sequence_triangulated_azimuth",
    "sequence_label",
    "pose_id",
    "camera_id",
    "camera_name",
]


def _parse_export_csv(body: str) -> Tuple[List[str], List[Dict[str, str]]]:
    reader = csv.DictReader(io.StringIO(body))
    rows = list(reader)
    return list(reader.fieldnames or []), rows


@pytest.mark.asyncio
async def test_alerts_export_happy_path(async_client: AsyncClient, detection_session: AsyncSession):
    base = datetime(2026, 4, 10, 12, 0, 0)
    alerts: List[Alert] = []
    for offset_days, (lat, lon) in enumerate([(48.1, 2.1), (48.2, 2.2), (48.3, 2.3)]):
        started = base + timedelta(days=offset_days)
        alert = await _create_alert(detection_session, 1, started, started + timedelta(minutes=5), lat, lon)
        await _attach_sequence(detection_session, alert)
        alerts.append(alert)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2026-04-10&to_date=2026-04-12",
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    assert resp.headers["content-type"].startswith("text/csv")
    assert "attachment" in resp.headers["content-disposition"]
    assert "alerts_2026-04-10_2026-04-12.csv" in resp.headers["content-disposition"]

    header, rows = _parse_export_csv(resp.text)
    assert header == _EXPORT_COLUMNS
    assert [int(r["alert_id"]) for r in rows] == [a.id for a in alerts]
    # ordering is ascending by alert.started_at
    started_iso = [f"{r['alert_started_at_date']}T{r['alert_started_at_time']}" for r in rows]
    assert started_iso == sorted(started_iso)
    first = rows[0]
    assert float(first["alert_triangulated_lat"]) == pytest.approx(48.1)
    assert float(first["alert_triangulated_lon"]) == pytest.approx(2.1)
    assert first["alert_started_at_date"] == alerts[0].started_at.date().isoformat()
    assert first["alert_started_at_time"] == alerts[0].started_at.time().isoformat()
    assert first["alert_last_seen_at"] == alerts[0].last_seen_at.isoformat()
    assert int(first["alert_duration_seconds"]) == int((alerts[0].last_seen_at - alerts[0].started_at).total_seconds())
    assert int(first["organization_id"]) == 1
    assert first["camera_name"] == "cam-1"
    assert first["sequence_label"] == "unknown"


@pytest.mark.asyncio
async def test_alerts_export_window_narrows(async_client: AsyncClient, detection_session: AsyncSession):
    base = datetime(2026, 4, 10, 12, 0, 0)
    a_before = await _create_alert(detection_session, 1, base, base + timedelta(minutes=5))
    await _attach_sequence(detection_session, a_before)
    a_in = await _create_alert(detection_session, 1, base + timedelta(days=1), base + timedelta(days=1, minutes=5))
    await _attach_sequence(detection_session, a_in)
    a_after = await _create_alert(detection_session, 1, base + timedelta(days=2), base + timedelta(days=2, minutes=5))
    await _attach_sequence(detection_session, a_after)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2026-04-11&to_date=2026-04-11",
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    _, rows = _parse_export_csv(resp.text)
    returned_ids = {int(r["alert_id"]) for r in rows}
    assert returned_ids == {a_in.id}


@pytest.mark.asyncio
async def test_alerts_export_org_isolation(async_client: AsyncClient, detection_session: AsyncSession):
    base = datetime(2026, 4, 10, 12, 0, 0)
    org1_alert = await _create_alert(detection_session, 1, base, base + timedelta(minutes=5))
    await _attach_sequence(detection_session, org1_alert, camera_id=1)
    org2_alert = await _create_alert(detection_session, 2, base, base + timedelta(minutes=5))
    await _attach_sequence(detection_session, org2_alert, camera_id=2)

    # Call as a non-admin user from org 1
    auth = pytest.get_token(
        pytest.user_table[1]["id"], pytest.user_table[1]["role"].split(), pytest.user_table[1]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2026-04-10&to_date=2026-04-10",
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    _, rows = _parse_export_csv(resp.text)
    returned_ids = {int(r["alert_id"]) for r in rows}
    assert org1_alert.id in returned_ids
    assert org2_alert.id not in returned_ids


@pytest.mark.asyncio
async def test_alerts_export_empty_range(async_client: AsyncClient, detection_session: AsyncSession):
    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2099-01-01&to_date=2099-01-31",
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    header, rows = _parse_export_csv(resp.text)
    assert header == _EXPORT_COLUMNS
    assert rows == []


@pytest.mark.asyncio
async def test_alerts_export_renders_null_coordinates_as_empty(
    async_client: AsyncClient, detection_session: AsyncSession
):
    base = datetime(2026, 4, 10, 12, 0, 0)
    alert = await _create_alert(detection_session, 1, base, base + timedelta(minutes=5), lat=None, lon=None)
    await _attach_sequence(detection_session, alert)

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2026-04-10&to_date=2026-04-10",
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    _, rows = _parse_export_csv(resp.text)
    row = next(r for r in rows if int(r["alert_id"]) == alert.id)
    assert row["alert_triangulated_lat"] == ""
    assert row["alert_triangulated_lon"] == ""


@pytest.mark.asyncio
async def test_alerts_export_invalid_range(async_client: AsyncClient, detection_session: AsyncSession):
    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2026-04-12&to_date=2026-04-10",
        headers=auth,
    )
    assert resp.status_code == 422, resp.text


@pytest.mark.asyncio
async def test_alerts_export_unauthenticated(async_client: AsyncClient, detection_session: AsyncSession):
    resp = await async_client.get("/alerts/export?from_date=2026-04-10&to_date=2026-04-12")
    assert resp.status_code == 401, resp.text


@pytest.mark.asyncio
async def test_alerts_export_emits_one_row_per_sequence(async_client: AsyncClient, detection_session: AsyncSession):
    base = datetime(2026, 4, 10, 12, 0, 0)
    alert = await _create_alert(detection_session, 1, base, base + timedelta(minutes=30))
    # Attach in non-monotonic order to verify the export sorts ASC by sequence.started_at.
    middle = await _attach_sequence(
        detection_session,
        alert,
        started_at=base + timedelta(minutes=10),
        last_seen_at=base + timedelta(minutes=20),
    )
    last = await _attach_sequence(
        detection_session,
        alert,
        started_at=base + timedelta(minutes=20),
        last_seen_at=base + timedelta(minutes=30),
    )
    first = await _attach_sequence(
        detection_session,
        alert,
        started_at=base,
        last_seen_at=base + timedelta(minutes=10),
    )

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2026-04-10&to_date=2026-04-10",
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    _, rows = _parse_export_csv(resp.text)
    alert_rows = [r for r in rows if int(r["alert_id"]) == alert.id]
    assert len(alert_rows) == 3
    assert [int(r["sequence_id"]) for r in alert_rows] == [first.id, middle.id, last.id]
    # Alert-level cells repeat across rows
    assert {r["alert_started_at_date"] for r in alert_rows} == {alert.started_at.date().isoformat()}
    assert {r["alert_last_seen_at"] for r in alert_rows} == {alert.last_seen_at.isoformat()}


@pytest.mark.asyncio
async def test_alerts_export_wildfire_label_mapping(async_client: AsyncClient, detection_session: AsyncSession):
    base = datetime(2026, 4, 10, 12, 0, 0)
    alert = await _create_alert(detection_session, 1, base, base + timedelta(minutes=30))
    wf = await _attach_sequence(
        detection_session,
        alert,
        is_wildfire=AnnotationType.WILDFIRE_SMOKE,
        started_at=base,
        last_seen_at=base + timedelta(minutes=10),
    )
    other = await _attach_sequence(
        detection_session,
        alert,
        is_wildfire=AnnotationType.OTHER_SMOKE,
        started_at=base + timedelta(minutes=10),
        last_seen_at=base + timedelta(minutes=20),
    )
    unk = await _attach_sequence(
        detection_session,
        alert,
        is_wildfire=None,
        started_at=base + timedelta(minutes=20),
        last_seen_at=base + timedelta(minutes=30),
    )

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2026-04-10&to_date=2026-04-10",
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    _, rows = _parse_export_csv(resp.text)
    label_by_seq = {int(r["sequence_id"]): r["sequence_label"] for r in rows if int(r["alert_id"]) == alert.id}
    assert label_by_seq == {wf.id: "wildfire", other.id: "other", unk.id: "unknown"}


@pytest.mark.asyncio
async def test_alerts_export_camera_name_resolution(async_client: AsyncClient, detection_session: AsyncSession):
    extra_camera = Camera(
        organization_id=1,
        name="cam-extra",
        angle_of_view=91.3,
        elevation=110.0,
        lat=3.7,
        lon=-45.3,
        is_trustable=True,
    )
    detection_session.add(extra_camera)
    await detection_session.commit()
    await detection_session.refresh(extra_camera)

    base = datetime(2026, 4, 10, 12, 0, 0)
    alert = await _create_alert(detection_session, 1, base, base + timedelta(minutes=20))
    seq_cam1 = await _attach_sequence(
        detection_session,
        alert,
        camera_id=1,
        started_at=base,
        last_seen_at=base + timedelta(minutes=10),
    )
    seq_extra = await _attach_sequence(
        detection_session,
        alert,
        camera_id=extra_camera.id,
        started_at=base + timedelta(minutes=10),
        last_seen_at=base + timedelta(minutes=20),
    )

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )
    resp = await async_client.get(
        "/alerts/export?from_date=2026-04-10&to_date=2026-04-10",
        headers=auth,
    )
    assert resp.status_code == 200, resp.text
    _, rows = _parse_export_csv(resp.text)
    cam_by_seq = {int(r["sequence_id"]): r["camera_name"] for r in rows if int(r["alert_id"]) == alert.id}
    assert cam_by_seq == {seq_cam1.id: "cam-1", seq_extra.id: "cam-extra"}
