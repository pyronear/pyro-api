# Copyright (C) 2025, Pyronear.
#
# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime, timedelta
from typing import List, Tuple

import pytest
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Alert, AlertSequence, Sequence


async def _create_alert_with_sequences(
    session: AsyncSession, org_id: int, camera_id: int, lat: float, lon: float
) -> Tuple[Alert, List[int]]:
    now = datetime.utcnow()
    seq_payloads = [
        dict(camera_id=camera_id, pose_id=None, azimuth=180.0, is_wildfire=None, cone_azimuth=163.4, cone_angle=1.0),
        dict(camera_id=camera_id, pose_id=None, azimuth=25.0, is_wildfire=None, cone_azimuth=8.3, cone_angle=0.8),
        dict(camera_id=camera_id, pose_id=None, azimuth=276.0, is_wildfire=None, cone_azimuth=276.5, cone_angle=3.0),
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
    alert, seq_ids = await _create_alert_with_sequences(
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
