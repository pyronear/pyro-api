# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import timedelta

import pytest  # type: ignore
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.time import utcnow
from app.models import Alert, AlertSequence, Sequence
from app.services.risk import risk_service


@pytest.fixture
def reset_risk_cache():
    previous = dict(risk_service._scores)
    risk_service._scores = {}
    yield
    risk_service._scores = previous


async def _seed_unlabeled_sequence(
    session: AsyncSession,
    camera_id: int,
    pose_id: int,
    max_conf: float,
    minutes_ago: int = 30,
) -> Sequence:
    now = utcnow()
    seq = Sequence(
        camera_id=camera_id,
        pose_id=pose_id,
        camera_azimuth=180.0,
        sequence_azimuth=175.0,
        cone_angle=5.0,
        is_wildfire=None,
        started_at=now - timedelta(minutes=minutes_ago),
        last_seen_at=now - timedelta(minutes=minutes_ago - 1),
        max_conf=max_conf,
    )
    session.add(seq)
    await session.commit()
    await session.refresh(seq)
    return seq


@pytest.mark.asyncio
async def test_unlabeled_latest_drops_low_conf_when_camera_is_low_risk(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    camera_id = pytest.camera_table[0]["id"]
    pose_id = pytest.pose_table[0]["id"]
    low_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.40, minutes_ago=30)
    high_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.55, minutes_ago=20)

    risk_service._scores = {camera_id: "low"}

    auth = pytest.get_token(
        pytest.user_table[0]["id"],
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )
    response = await async_client.get("/sequences/unlabeled/latest", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    returned_ids = {item["id"] for item in response.json()}
    assert low_seq.id not in returned_ids
    assert high_seq.id in returned_ids


@pytest.mark.asyncio
async def test_unlabeled_latest_drops_below_very_low_threshold(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    camera_id = pytest.camera_table[0]["id"]
    pose_id = pytest.pose_table[0]["id"]
    # 0.55 passes the low threshold (0.45) but fails very_low (0.6)
    seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.55, minutes_ago=25)

    risk_service._scores = {camera_id: "very_low"}

    auth = pytest.get_token(
        pytest.user_table[0]["id"],
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )
    response = await async_client.get("/sequences/unlabeled/latest", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert seq.id not in {item["id"] for item in response.json()}


@pytest.mark.asyncio
async def test_unlabeled_latest_keeps_all_when_class_is_moderate(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    camera_id = pytest.camera_table[0]["id"]
    pose_id = pytest.pose_table[0]["id"]
    low_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.10, minutes_ago=30)

    risk_service._scores = {camera_id: "moderate"}

    auth = pytest.get_token(
        pytest.user_table[0]["id"],
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )
    response = await async_client.get("/sequences/unlabeled/latest", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert low_seq.id in {item["id"] for item in response.json()}


async def _seed_alert_with_sequence(session: AsyncSession, organization_id: int, seq: Sequence) -> Alert:
    now = utcnow()
    alert = Alert(
        organization_id=organization_id,
        started_at=now - timedelta(minutes=20),
        last_seen_at=now - timedelta(minutes=19),
    )
    session.add(alert)
    await session.commit()
    await session.refresh(alert)
    session.add(AlertSequence(alert_id=alert.id, sequence_id=seq.id))
    await session.commit()
    return alert


@pytest.mark.asyncio
async def test_alerts_unlabeled_latest_drops_alert_when_all_seqs_below_threshold(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    camera_id = pytest.camera_table[1]["id"]  # belongs to org 2 (user_idx 2)
    pose_id = pytest.pose_table[2]["id"]
    seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.30, minutes_ago=20)
    alert = await _seed_alert_with_sequence(detection_session, organization_id=2, seq=seq)

    risk_service._scores = {camera_id: "low"}

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get("/alerts/unlabeled/latest", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert alert.id not in {item["id"] for item in response.json()}


@pytest.mark.asyncio
async def test_alerts_unlabeled_latest_risk_score_override(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.30, minutes_ago=20)
    alert = await _seed_alert_with_sequence(detection_session, organization_id=2, seq=seq)

    # Risk-api would say "moderate" (no filter), but the override forces "low" -> 0.45 threshold drops it.
    risk_service._scores = {camera_id: "moderate"}

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get("/alerts/unlabeled/latest?risk_score=low", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert alert.id not in {item["id"] for item in response.json()}


@pytest.mark.asyncio
async def test_alerts_unlabeled_latest_risk_score_moderate_keeps_everything(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.10, minutes_ago=20)
    alert = await _seed_alert_with_sequence(detection_session, organization_id=2, seq=seq)

    # Cache says very_low (would drop everything), but the override forces moderate.
    risk_service._scores = {camera_id: "very_low"}

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get("/alerts/unlabeled/latest?risk_score=moderate", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert alert.id in {item["id"] for item in response.json()}


@pytest.mark.asyncio
async def test_alerts_unlabeled_latest_risk_score_invalid_value_returns_422(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get("/alerts/unlabeled/latest?risk_score=bogus", headers=auth)
    assert response.status_code == 422
