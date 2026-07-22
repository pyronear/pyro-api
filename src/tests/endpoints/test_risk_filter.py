# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import date, timedelta
from unittest.mock import AsyncMock, patch

import pytest  # type: ignore
from httpx import AsyncClient
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints.alerts import fetch_alerts_from_date
from app.core.time import utcnow
from app.models import Alert, AlertSequence, Sequence, UserRole
from app.schemas.login import TokenPayload
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
@pytest.mark.parametrize("fwi_class", ["moderate", "high", "very_high", "extreme"])
async def test_unlabeled_latest_keeps_all_when_class_is_moderate_or_above(
    fwi_class: str, async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """No filter is applied for ``moderate`` and above; pin every class so future tweaks stay covered."""
    camera_id = pytest.camera_table[0]["id"]
    pose_id = pytest.pose_table[0]["id"]
    low_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.10, minutes_ago=30)

    risk_service._scores = {camera_id: fwi_class}

    auth = pytest.get_token(
        pytest.user_table[0]["id"],
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )
    response = await async_client.get("/sequences/unlabeled/latest", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert low_seq.id in {item["id"] for item in response.json()}


@pytest.mark.asyncio
async def test_unlabeled_latest_keeps_seq_with_null_max_conf_under_filter(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """Sequences with NULL max_conf (legacy / unparseable bbox) must pass even under an active filter."""
    camera_id = pytest.camera_table[0]["id"]
    pose_id = pytest.pose_table[0]["id"]
    null_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=None, minutes_ago=20)  # type: ignore[arg-type]

    risk_service._scores = {camera_id: "low"}  # 0.45 threshold, would normally drop

    auth = pytest.get_token(
        pytest.user_table[0]["id"],
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )
    response = await async_client.get("/sequences/unlabeled/latest", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert null_seq.id in {item["id"] for item in response.json()}


@pytest.mark.asyncio
async def test_unlabeled_latest_keeps_seq_for_camera_unknown_to_risk_api(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """A camera absent from the risk-api cache stays unfiltered even when sibling cameras are filtered."""
    known_cam = pytest.camera_table[0]["id"]
    unknown_cam = pytest.camera_table[1]["id"]
    known_pose = pytest.pose_table[0]["id"]
    unknown_pose = pytest.pose_table[2]["id"]

    # Cache only knows about ``known_cam`` and flags it ``low`` (0.45 threshold).
    # ``unknown_cam`` has no entry -> CASE else_=0.0 -> any max_conf passes.
    risk_service._scores = {known_cam: "low"}

    known_dropped = await _seed_unlabeled_sequence(detection_session, known_cam, known_pose, max_conf=0.20)
    unknown_kept = await _seed_unlabeled_sequence(detection_session, unknown_cam, unknown_pose, max_conf=0.10)

    # known_cam belongs to org 1; unknown_cam belongs to org 2 -> query both orgs.
    auth_org1 = pytest.get_token(
        pytest.user_table[0]["id"],
        pytest.user_table[0]["role"].split(),
        pytest.user_table[0]["organization_id"],
    )
    auth_org2 = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )

    resp1 = await async_client.get("/sequences/unlabeled/latest", headers=auth_org1)
    assert resp1.status_code == 200, print(resp1.__dict__)
    assert known_dropped.id not in {item["id"] for item in resp1.json()}

    resp2 = await async_client.get("/sequences/unlabeled/latest", headers=auth_org2)
    assert resp2.status_code == 200, print(resp2.__dict__)
    assert unknown_kept.id in {item["id"] for item in resp2.json()}


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
async def test_alerts_unlabeled_latest_count_matches_list_under_risk_filter(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """The count endpoint must apply the same risk_score filter as the list, so the two stay in sync."""
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    low_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.30, minutes_ago=20)
    high_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.55, minutes_ago=15)
    await _seed_alert_with_sequence(detection_session, organization_id=2, seq=low_seq)
    kept_alert = await _seed_alert_with_sequence(detection_session, organization_id=2, seq=high_seq)

    risk_service._scores = {camera_id: "moderate"}  # no filter from the cache; override drives the filter

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )

    # low threshold (0.45) drops the 0.30 alert but keeps the 0.55 one.
    count_resp = await async_client.get("/alerts/unlabeled/latest/count?risk_score=low", headers=auth)
    assert count_resp.status_code == 200, print(count_resp.__dict__)
    assert count_resp.json() == {"count": 1}

    list_resp = await async_client.get("/alerts/unlabeled/latest?risk_score=low&limit=100", headers=auth)
    assert list_resp.status_code == 200, print(list_resp.__dict__)
    list_ids = [item["id"] for item in list_resp.json()]
    assert list_ids == [kept_alert.id]
    assert count_resp.json()["count"] == len(list_ids)

    # Without the override the cache class is moderate (no filter): both alerts count.
    count_resp = await async_client.get("/alerts/unlabeled/latest/count", headers=auth)
    assert count_resp.status_code == 200, print(count_resp.__dict__)
    assert count_resp.json() == {"count": 2}


@pytest.mark.asyncio
@pytest.mark.parametrize("fwi_class", ["moderate", "high", "very_high", "extreme"])
async def test_alerts_unlabeled_latest_risk_score_moderate_or_above_keeps_everything(
    fwi_class: str, async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """Override at any moderate-or-above class disables the filter even when the cache would drop the alert."""
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.10, minutes_ago=20)
    alert = await _seed_alert_with_sequence(detection_session, organization_id=2, seq=seq)

    # Cache says very_low (would drop everything), but the override forces a no-filter class.
    risk_service._scores = {camera_id: "very_low"}

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get(f"/alerts/unlabeled/latest?risk_score={fwi_class}", headers=auth)
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


@pytest.mark.asyncio
async def test_sequences_unlabeled_latest_risk_score_override_drops_low_conf(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    low_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.30, minutes_ago=20)
    high_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.55, minutes_ago=15)

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get("/sequences/unlabeled/latest?risk_score=low", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    returned_ids = {item["id"] for item in response.json()}
    assert low_seq.id not in returned_ids
    assert high_seq.id in returned_ids


@pytest.mark.asyncio
async def test_sequences_unlabeled_latest_risk_score_invalid_value_returns_422(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get("/sequences/unlabeled/latest?risk_score=bogus", headers=auth)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_sequences_fromdate_risk_score_moderate_disables_filter(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """``risk_score=moderate`` is the kill switch: every seed seq comes back regardless of max_conf."""
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    target_date = utcnow().date().isoformat()

    seeded = []
    for max_conf, minutes_ago in [(0.05, 50), (0.20, 45), (0.55, 30)]:
        seq = await _seed_unlabeled_sequence(
            detection_session, camera_id, pose_id, max_conf=max_conf, minutes_ago=minutes_ago
        )
        seeded.append(seq.id)

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get(
        f"/sequences/all/fromdate?from_date={target_date}&limit=200&risk_score=moderate", headers=auth
    )
    assert response.status_code == 200, print(response.__dict__)
    returned_ids = {item["id"] for item in response.json()}
    assert set(seeded).issubset(returned_ids)


@pytest.mark.asyncio
async def test_alerts_unlabeled_latest_keeps_alert_with_mixed_seqs(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """An alert mixing one passing and one failing sequence stays, with only the passing seq in payload."""
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    low_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.30, minutes_ago=25)
    high_seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.70, minutes_ago=15)

    now = utcnow()
    alert = Alert(
        organization_id=2,
        started_at=now - timedelta(minutes=30),
        last_seen_at=now - timedelta(minutes=10),
    )
    detection_session.add(alert)
    await detection_session.commit()
    await detection_session.refresh(alert)
    detection_session.add(AlertSequence(alert_id=alert.id, sequence_id=low_seq.id))
    detection_session.add(AlertSequence(alert_id=alert.id, sequence_id=high_seq.id))
    await detection_session.commit()

    risk_service._scores = {camera_id: "low"}  # 0.45 threshold

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get("/alerts/unlabeled/latest", headers=auth)
    assert response.status_code == 200, print(response.__dict__)

    payload = next((a for a in response.json() if a["id"] == alert.id), None)
    assert payload is not None, "alert with at least one passing sequence must remain"
    seq_ids = {s["id"] for s in payload["sequences"]}
    assert high_seq.id in seq_ids
    assert low_seq.id not in seq_ids


@pytest.mark.asyncio
async def test_alerts_fromdate_risk_score_override_drops_low_conf_alert(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    target_date = utcnow().date().isoformat()
    seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.30, minutes_ago=20)
    alert = await _seed_alert_with_sequence(detection_session, organization_id=2, seq=seq)

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get(f"/alerts/all/fromdate?from_date={target_date}&risk_score=low", headers=auth)
    assert response.status_code == 200, print(response.__dict__)
    assert alert.id not in {item["id"] for item in response.json()}


@pytest.mark.asyncio
@pytest.mark.parametrize("fwi_class", ["moderate", "high", "very_high", "extreme"])
async def test_alerts_fromdate_risk_score_moderate_or_above_keeps_alert(
    fwi_class: str, async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """No-filter override (``moderate`` and above) keeps the alert on ``/alerts/all/fromdate`` too."""
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    target_date = utcnow().date().isoformat()
    seq = await _seed_unlabeled_sequence(detection_session, camera_id, pose_id, max_conf=0.10, minutes_ago=20)
    alert = await _seed_alert_with_sequence(detection_session, organization_id=2, seq=seq)

    # Cache says very_low (would drop everything), but the override forces a no-filter class.
    risk_service._scores = {camera_id: "very_low"}

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get(
        f"/alerts/all/fromdate?from_date={target_date}&risk_score={fwi_class}", headers=auth
    )
    assert response.status_code == 200, print(response.__dict__)
    assert alert.id in {item["id"] for item in response.json()}


@pytest.mark.asyncio
async def test_alerts_fromdate_risk_score_invalid_value_returns_422(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    target_date = utcnow().date().isoformat()
    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )
    response = await async_client.get(f"/alerts/all/fromdate?from_date={target_date}&risk_score=bogus", headers=auth)
    assert response.status_code == 422


class _ExecResult:
    def __init__(self, rows) -> None:
        self._rows = rows

    def all(self):
        return self._rows


class _FakeAlertsSession:
    def __init__(self, *results) -> None:
        self._results = list(results)
        self.statements = []

    async def exec(self, stmt):
        self.statements.append(stmt)
        return self._results.pop(0)


def _unit_token(organization_id: int = 1) -> TokenPayload:
    return TokenPayload(sub=1, scopes=[UserRole.USER], organization_id=organization_id)


@pytest.mark.asyncio
async def test_unit_fetch_alerts_from_date_calls_risk_scores_for_requested_date():
    """The per-date branch must dispatch ``get_scores_for_date`` with the requested date and org."""
    target_date = date(2026, 5, 5)
    now = utcnow()
    alert = Alert(id=501, organization_id=1, started_at=now, last_seen_at=now)
    seq = Sequence(
        id=601,
        camera_id=1,
        pose_id=1,
        camera_azimuth=180.0,
        sequence_azimuth=175.0,
        cone_angle=5.0,
        is_wildfire=None,
        started_at=now - timedelta(minutes=20),
        last_seen_at=now - timedelta(minutes=5),
        max_conf=0.70,
    )
    session = _FakeAlertsSession(_ExecResult([alert]), _ExecResult([(alert.id, seq)]))
    risk_scores_mock = AsyncMock(return_value={})  # empty -> no SQL filter, simpler stmt order
    counts_mock = AsyncMock(return_value={seq.id: 3})

    with (
        patch("app.api.api_v1.endpoints.alerts.risk_service.get_scores_for_date", new=risk_scores_mock),
        patch("app.api.api_v1.endpoints.alerts.get_detection_counts_by_sequence_ids", new=counts_mock),
    ):
        result = await fetch_alerts_from_date(
            from_date=target_date,
            limit=10,
            offset=0,
            risk_score=None,
            session=session,
            token_payload=_unit_token(),
        )

    risk_scores_mock.assert_awaited_once_with(target_date, organization_id=1)
    counts_mock.assert_awaited_once_with(session, [seq.id])
    assert [item.id for item in result] == [alert.id]
    assert [s.id for s in result[0].sequences] == [seq.id]


@pytest.mark.asyncio
async def test_unit_fetch_alerts_from_date_risk_score_override_bypasses_risk_api():
    """The override branch must NOT hit the risk API and must apply the override class to all org cameras."""
    target_date = date(2026, 5, 5)
    now = utcnow()
    alert = Alert(id=502, organization_id=1, started_at=now, last_seen_at=now)
    seq = Sequence(
        id=602,
        camera_id=1,
        pose_id=1,
        camera_azimuth=180.0,
        sequence_azimuth=175.0,
        cone_angle=5.0,
        is_wildfire=None,
        started_at=now - timedelta(minutes=20),
        last_seen_at=now - timedelta(minutes=5),
        max_conf=0.55,
    )
    # Override path -> first exec: select Camera.id, then alerts_stmt, then alert_seq map
    session = _FakeAlertsSession(
        _ExecResult([1]),
        _ExecResult([alert]),
        _ExecResult([(alert.id, seq)]),
    )
    risk_scores_mock = AsyncMock()
    counts_mock = AsyncMock(return_value={seq.id: 1})

    with (
        patch("app.api.api_v1.endpoints.alerts.risk_service.get_scores_for_date", new=risk_scores_mock),
        patch("app.api.api_v1.endpoints.alerts.get_detection_counts_by_sequence_ids", new=counts_mock),
    ):
        result = await fetch_alerts_from_date(
            from_date=target_date,
            limit=10,
            offset=0,
            risk_score="low",
            session=session,
            token_payload=_unit_token(),
        )

    risk_scores_mock.assert_not_awaited()
    assert [item.id for item in result] == [alert.id]
    assert [s.id for s in result[0].sequences] == [seq.id]


@pytest.mark.asyncio
async def test_sequences_fromdate_pagination_filters_before_limit(
    async_client: AsyncClient, detection_session: AsyncSession, reset_risk_cache
):
    """A page must come back full when the filter would otherwise consume the whole limit."""
    camera_id = pytest.camera_table[1]["id"]
    pose_id = pytest.pose_table[2]["id"]
    target_date = utcnow().date().isoformat()

    # 2 below threshold + 3 above. With LIMIT 3, naive post-filter would return at most 1.
    for max_conf, minutes_ago in [(0.10, 50), (0.20, 45), (0.50, 40), (0.60, 35), (0.80, 30)]:
        await _seed_unlabeled_sequence(
            detection_session, camera_id, pose_id, max_conf=max_conf, minutes_ago=minutes_ago
        )

    auth = pytest.get_token(
        pytest.user_table[2]["id"],
        pytest.user_table[2]["role"].split(),
        pytest.user_table[2]["organization_id"],
    )

    # The ``risk_score=low`` override drives the threshold without hitting the risk API.
    response = await async_client.get(
        f"/sequences/all/fromdate?from_date={target_date}&limit=3&risk_score=low", headers=auth
    )
    assert response.status_code == 200, print(response.__dict__)
    page = response.json()
    assert len(page) == 3
    assert all(seq["max_conf"] >= 0.45 for seq in page)
