# Copyright (C) 2025, Pyronear.
#
# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime, timedelta
from typing import Any, List, Tuple, cast

import pandas as pd
import pytest  # type: ignore
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Alert, AlertSequence, AnnotationType, Camera, Sequence
from app.services.overlap import compute_overlap


async def _create_alert_with_sequences(
    session: AsyncSession, org_id: int, camera_id: int, lat: float, lon: float
) -> Tuple[Alert, List[int]]:
    now = datetime.utcnow()
    seq_payloads = [
        {
            "camera_id": camera_id,
            "pose_id": None,
            "azimuth": 180.0,
            "is_wildfire": None,
            "cone_azimuth": 163.4,
            "cone_angle": 1.0,
        },
        {
            "camera_id": camera_id,
            "pose_id": None,
            "azimuth": 25.0,
            "is_wildfire": None,
            "cone_azimuth": 8.3,
            "cone_angle": 0.8,
        },
        {
            "camera_id": camera_id,
            "pose_id": None,
            "azimuth": 276.0,
            "is_wildfire": None,
            "cone_azimuth": 276.5,
            "cone_angle": 3.0,
        },
    ]
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
    return alert, [seq.id for seq in sequences]


@pytest.mark.asyncio
async def test_get_alert_and_sequences(async_client: AsyncClient, detection_session: AsyncSession):
    alert, _seq_ids = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )

    resp = await async_client.get(f"/alerts/{alert.id}", headers=auth)
    assert resp.status_code == 200, resp.text
    assert resp.json()["id"] == alert.id
    assert resp.json()["lat"] == pytest.approx(alert.lat)
    assert resp.json()["lon"] == pytest.approx(alert.lon)
    assert resp.json()["started_at"] == alert.started_at.isoformat()
    assert resp.json()["last_seen_at"] == alert.last_seen_at.isoformat()

    resp = await async_client.get(f"/alerts/{alert.id}/sequences?limit=5&desc=true", headers=auth)
    assert resp.status_code == 200, resp.text
    returned = resp.json()
    last_seen_times = [item["last_seen_at"] for item in returned]
    assert last_seen_times == sorted(last_seen_times, reverse=True)


@pytest.mark.asyncio
async def test_alerts_unlabeled_latest(async_client: AsyncClient, detection_session: AsyncSession):
    alert, _ = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )

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


@pytest.mark.asyncio
async def test_alerts_from_date(async_client: AsyncClient, detection_session: AsyncSession):
    alert, _ = await _create_alert_with_sequences(
        detection_session, org_id=1, camera_id=1, lat=48.3856355, lon=2.7323256
    )
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


@pytest.mark.asyncio
async def test_alert_recompute_after_sequence_relabel(async_client: AsyncClient, detection_session: AsyncSession):
    # Build three overlapping sequences on the same camera
    now = datetime.utcnow()
    camera_id = 1
    seq_specs = [
        {"azimuth": 0.0, "cone_azimuth": 0.0, "cone_angle": 20.0, "offset": 2},
        {"azimuth": 5.0, "cone_azimuth": 5.0, "cone_angle": 20.0, "offset": 1},
        {"azimuth": 350.0, "cone_azimuth": 350.0, "cone_angle": 20.0, "offset": 0},
    ]
    seqs: List[Sequence] = []
    for spec in seq_specs:
        seq = Sequence(
            camera_id=camera_id,
            pose_id=None,
            azimuth=spec["azimuth"],
            is_wildfire=None,
            cone_azimuth=spec["cone_azimuth"],
            cone_angle=spec["cone_angle"],
            started_at=now - timedelta(seconds=10 + spec["offset"]),
            last_seen_at=now - timedelta(seconds=spec["offset"]),
        )
        detection_session.add(seq)
        seqs.append(seq)
    await detection_session.commit()
    for seq in seqs:
        await detection_session.refresh(seq)

    # Compute initial alert location from all three
    camera = await detection_session.get(Camera, camera_id)
    assert camera is not None
    records = [
        {
            "id": seq.id,
            "lat": camera.lat,
            "lon": camera.lon,
            "cone_azimuth": seq.cone_azimuth,
            "cone_angle": seq.cone_angle,
            "is_wildfire": seq.is_wildfire,
            "started_at": seq.started_at,
            "last_seen_at": seq.last_seen_at,
        }
        for seq in seqs
    ]
    df_all = compute_overlap(pd.DataFrame.from_records(records))
    initial_loc = next((loc for locs in df_all["event_smoke_locations"].tolist() for loc in locs if loc is not None), None)

    alert = Alert(
        organization_id=1,
        lat=initial_loc[0] if initial_loc else None,
        lon=initial_loc[1] if initial_loc else None,
        started_at=min(seq.started_at for seq in seqs),
        last_seen_at=max(seq.last_seen_at for seq in seqs),
    )
    detection_session.add(alert)
    await detection_session.commit()
    await detection_session.refresh(alert)

    for seq in seqs:
        detection_session.add(AlertSequence(alert_id=alert.id, sequence_id=seq.id))
    await detection_session.commit()

    auth = pytest.get_token(
        pytest.user_table[0]["id"], pytest.user_table[0]["role"].split(), pytest.user_table[0]["organization_id"]
    )

    # Relabel one sequence as non-wildfire -> should be detached, new alert created, old alert recomputed
    target_seq = seqs[-1]
    resp = await async_client.patch(
        f"/sequences/{target_seq.id}/label",
        json={"is_wildfire": AnnotationType.OTHER_SMOKE.value},
        headers=auth,
    )
    assert resp.status_code == 200, resp.text

    # Fetch alerts and mappings with fresh values
    alerts_res = await detection_session.exec(select(Alert).execution_options(populate_existing=True))
    alerts_in_db = alerts_res.all()
    assert len(alerts_in_db) == 2

    mappings_res = await detection_session.exec(
        select(AlertSequence.alert_id, AlertSequence.sequence_id).execution_options(populate_existing=True)
    )
    mappings = mappings_res.all()

    # Identify alerts
    new_alert = next(a for a in alerts_in_db if a.id != alert.id)
    updated_alert = next(a for a in alerts_in_db if a.id == alert.id)

    # New alert should only reference relabeled sequence
    assert (new_alert.id, target_seq.id) in mappings
    assert updated_alert.id != new_alert.id

    # Updated alert should only reference remaining sequences
    remaining_ids = {seqs[0].id, seqs[1].id}
    remaining_mappings = {(aid, sid) for aid, sid in mappings if aid == updated_alert.id}
    assert remaining_mappings == {(updated_alert.id, sid) for sid in remaining_ids}

    # Reload remaining sequences from DB to compare times
    remaining_seqs_res = await detection_session.exec(
        select(Sequence)
        .where(cast(Any, Sequence.id).in_(list(remaining_ids)))
        .execution_options(populate_existing=True)
    )
    remaining_seqs = remaining_seqs_res.all()

    # Updated alert times recomputed
    assert updated_alert.started_at == min(seq.started_at for seq in remaining_seqs)
    assert updated_alert.last_seen_at == max(seq.last_seen_at for seq in remaining_seqs)

    # Updated alert location recomputed from remaining sequences
    remaining_records = [
        {
            "id": seq.id,
            "lat": camera.lat,
            "lon": camera.lon,
            "cone_azimuth": seq.cone_azimuth,
            "cone_angle": seq.cone_angle,
            "is_wildfire": seq.is_wildfire,
            "started_at": seq.started_at,
            "last_seen_at": seq.last_seen_at,
        }
        for seq in remaining_seqs
    ]
    df_remaining = compute_overlap(pd.DataFrame.from_records(remaining_records))
    remaining_loc = next(
        (loc for locs in df_remaining["event_smoke_locations"].tolist() for loc in locs if loc is not None), None
    )
    if remaining_loc:
        assert updated_alert.lat == pytest.approx(remaining_loc[0])
        assert updated_alert.lon == pytest.approx(remaining_loc[1])
