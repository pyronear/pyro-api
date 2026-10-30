from datetime import datetime, timedelta
from typing import List, Union

import pytest
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints.detections import _merge_alerts
from app.core.config import settings
from app.core.security import hash_share_token
from app.core.time import utcnow
from app.crud import AlertCRUD
from app.models import Alert, AlertShare, Detection


def _auth(user_idx: Union[int, None]):
    if user_idx is None:
        return None
    return pytest.get_token(
        pytest.user_table[user_idx]["id"],
        pytest.user_table[user_idx]["role"].split(),
        pytest.user_table[user_idx]["organization_id"],
    )


@pytest.mark.parametrize(
    ("user_idx", "alert_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (1, 1, 201, None),
        (2, 1, 403, "Access forbidden."),
        (1, 99, 404, "Table Alert has no corresponding entry."),
        # Admins can share any organization's alert
        (0, 2, 201, None),
    ],
)
@pytest.mark.asyncio
async def test_create_share(
    async_client: AsyncClient,
    share_session: AsyncSession,
    user_idx: Union[int, None],
    alert_id: int,
    status_code: int,
    status_detail: Union[str, None],
):
    response = await async_client.post("/shares", json={"alert_id": alert_id}, headers=_auth(user_idx))
    assert response.status_code == status_code, response.text
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code == 201:
        payload = response.json()
        assert payload["alert_id"] == alert_id
        assert len(payload["token"]) >= 43
        expires_at = datetime.fromisoformat(payload["expires_at"])
        assert abs(expires_at - (utcnow() + timedelta(hours=settings.SHARE_EXPIRE_HOURS))) < timedelta(minutes=1)
        share = await share_session.get(AlertShare, payload["share_id"])
        assert share is not None
        # Only the hash is stored, and it matches the token handed out
        assert share.token_hash == hash_share_token(payload["token"])
        assert share.created_by == pytest.user_table[user_idx]["id"]
        assert share.organization_id == pytest.alert_table[alert_id - 1]["organization_id"]


@pytest.mark.parametrize(
    ("user_idx", "alert_id", "expected_ids"),
    [
        (1, None, [3, 2, 1]),
        (2, None, [4]),
        (0, None, [4, 3, 2, 1]),
        (1, 1, [3, 2, 1]),
        (1, 2, []),
    ],
)
@pytest.mark.asyncio
async def test_fetch_shares(
    async_client: AsyncClient,
    share_session: AsyncSession,
    user_idx: int,
    alert_id: Union[int, None],
    expected_ids: List[int],
):
    params = {} if alert_id is None else {"alert_id": alert_id}
    response = await async_client.get("/shares", params=params, headers=_auth(user_idx))
    assert response.status_code == 200, response.text
    payload = response.json()
    assert [entry["id"] for entry in payload] == expected_ids
    statuses = {1: "active", 2: "expired", 3: "revoked", 4: "active"}
    for entry in payload:
        assert entry["status"] == statuses[entry["id"]]
        assert "token" not in entry
        assert "token_hash" not in entry


@pytest.mark.asyncio
async def test_fetch_shares_requires_auth(async_client: AsyncClient, share_session: AsyncSession):
    response = await async_client.get("/shares")
    assert response.status_code == 401


@pytest.mark.parametrize(
    ("user_idx", "share_id", "status_code", "status_detail"),
    [
        (None, 1, 401, "Not authenticated"),
        (1, 1, 200, None),
        (2, 1, 403, "Access forbidden."),
        (1, 99, 404, "Table AlertShare has no corresponding entry."),
        (0, 4, 200, None),
    ],
)
@pytest.mark.asyncio
async def test_revoke_share(
    async_client: AsyncClient,
    share_session: AsyncSession,
    user_idx: Union[int, None],
    share_id: int,
    status_code: int,
    status_detail: Union[str, None],
):
    response = await async_client.delete(f"/shares/{share_id}", headers=_auth(user_idx))
    assert response.status_code == status_code, response.text
    if isinstance(status_detail, str):
        assert response.json()["detail"] == status_detail
    if response.status_code == 200:
        payload = response.json()
        assert payload["status"] == "revoked"
        # Cancelling twice keeps the first cancellation time
        again = await async_client.delete(f"/shares/{share_id}", headers=_auth(user_idx))
        assert again.status_code == 200
        assert again.json()["revoked_at"] == payload["revoked_at"]


@pytest.mark.asyncio
async def test_public_shared_alert(async_client: AsyncClient, share_session: AsyncSession):
    response = await async_client.get(f"/shares/public/{pytest.share_tokens[0]}")
    assert response.status_code == 200, response.text
    assert response.headers["cache-control"] == "no-store"
    payload = response.json()
    assert set(payload) == {"started_at", "last_seen_at", "lat", "lon", "expires_at", "sequences"}
    assert (payload["lat"], payload["lon"]) == (pytest.alert_table[0]["lat"], pytest.alert_table[0]["lon"])
    assert len(payload["sequences"]) == 1
    sequence = payload["sequences"][0]
    assert set(sequence) == {
        "started_at",
        "last_seen_at",
        "camera_azimuth",
        "sequence_azimuth",
        "cone_angle",
        "camera",
        "detections",
    }
    # Camera position only: no id, organization nor device addresses
    assert set(sequence["camera"]) == {"name", "lat", "lon", "elevation", "angle_of_view"}
    assert sequence["camera"]["name"] == pytest.camera_table[0]["name"]
    assert len(sequence["detections"]) == 3
    for detection in sequence["detections"]:
        assert set(detection) == {"recorded_at", "bbox", "url"}
        assert detection["url"].startswith("http")
    # Newest first
    recorded = [detection["recorded_at"] for detection in sequence["detections"]]
    assert recorded == sorted(recorded, reverse=True)


@pytest.mark.parametrize(
    ("token", "status_code", "status_detail"),
    [
        ("unknown-token", 404, "Share link not found."),
        (pytest.share_tokens[1], 410, "Share link expired."),
        (pytest.share_tokens[2], 410, "Share link expired."),
    ],
)
@pytest.mark.asyncio
async def test_public_shared_alert_unavailable(
    async_client: AsyncClient, share_session: AsyncSession, token: str, status_code: int, status_detail: str
):
    response = await async_client.get(f"/shares/public/{token}")
    assert response.status_code == status_code, response.text
    assert response.json()["detail"] == status_detail


@pytest.mark.asyncio
async def test_public_shared_alert_after_revoke(async_client: AsyncClient, share_session: AsyncSession):
    token = pytest.share_tokens[0]
    before = await async_client.get(f"/shares/public/{token}")
    assert before.status_code == 200
    revoked = await async_client.delete("/shares/1", headers=_auth(1))
    assert revoked.status_code == 200
    after = await async_client.get(f"/shares/public/{token}")
    assert after.status_code == 410


@pytest.mark.asyncio
async def test_public_shared_alert_skips_continuity_frames(async_client: AsyncClient, share_session: AsyncSession):
    share_session.add(
        Detection(
            camera_id=1,
            pose_id=1,
            sequence_id=1,
            bucket_key="my_file",
            bbox="[]",
            created_at=datetime.strptime("2023-11-07T15:38:19.226673", "%Y-%m-%dT%H:%M:%S.%f"),
        )
    )
    await share_session.commit()
    response = await async_client.get(f"/shares/public/{pytest.share_tokens[0]}")
    assert response.status_code == 200
    detections = response.json()["sequences"][0]["detections"]
    assert len(detections) == 3
    assert all(detection["bbox"] != "[]" for detection in detections)


@pytest.mark.asyncio
async def test_deleting_shared_alert_removes_its_shares(async_client: AsyncClient, share_session: AsyncSession):
    response = await async_client.delete("/alerts/1", headers=_auth(0))
    assert response.status_code == 200, response.text
    remaining = (await share_session.exec(select(AlertShare.id))).all()
    assert sorted(remaining) == [4]
    public = await async_client.get(f"/shares/public/{pytest.share_tokens[0]}")
    assert public.status_code == 404


@pytest.mark.asyncio
async def test_merge_moves_shares_to_surviving_alert(async_client: AsyncClient, share_session: AsyncSession):
    alert_crud = AlertCRUD(share_session)
    now = utcnow()
    target = Alert(organization_id=1, lat=None, lon=None, started_at=now, last_seen_at=now)
    share_session.add(target)
    await share_session.commit()
    await share_session.refresh(target)

    await _merge_alerts(target.id, {1}, alert_crud)
    await share_session.commit()

    shares = (await share_session.exec(select(AlertShare).where(AlertShare.organization_id == 1))).all()
    assert {share.alert_id for share in shares} == {target.id}
    response = await async_client.get(f"/shares/public/{pytest.share_tokens[0]}")
    assert response.status_code == 200, response.text
    # The merged alert carries the absorbed alert's sequence
    assert len(response.json()["sequences"]) == 1
