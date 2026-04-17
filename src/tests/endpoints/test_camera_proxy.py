from unittest.mock import AsyncMock, patch

import pytest
import pytest_asyncio
from fastapi import HTTPException
from httpx import AsyncClient
from PIL import Image
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import Camera

# A camera that has device_ip and camera_ip configured (org1, so admin & agent can access it).
CONFIGURED_CAM_ID = 10
CONFIGURED_CAM = {
    "id": CONFIGURED_CAM_ID,
    "organization_id": 1,
    "name": "cam-configured",
    "angle_of_view": 90.0,
    "elevation": 100.0,
    "lat": 44.0,
    "lon": 4.0,
    "device_ip": "192.168.1.100",
    "camera_ip": "192.168.1.101",
}

# Fake JPEG bytes (minimal valid header is enough for content-type tests)
FAKE_JPEG = b"\xff\xd8\xff" + b"\x00" * 64

_PROXY_MODULE = "app.api.api_v1.endpoints.camera_proxy"


@pytest_asyncio.fixture()
async def configured_camera_session(camera_session: AsyncSession):
    """camera_session extended with one camera that has device_ip / camera_ip set."""
    camera_session.add(Camera(**CONFIGURED_CAM))
    await camera_session.commit()
    yield camera_session
    await camera_session.rollback()


def _auth(user_idx: int) -> dict:
    return pytest.get_token(
        pytest.user_table[user_idx]["id"],
        pytest.user_table[user_idx]["role"].split(),
        pytest.user_table[user_idx]["organization_id"],
    )


# ── Auth / Organisation isolation ─────────────────────────────────────────────
#
# Users in conftest:
#   [0] admin  - org 1
#   [1] agent  - org 1
#   [2] user   - org 2
#
# Cameras in conftest (no device_ip / camera_ip):
#   id=1  org 1  (cam-1)
#   id=2  org 2  (cam-2)
#
# Expected flow for a correctly-scoped caller on a cam without device config:
#   auth passes → org check passes → _device_config raises 409
# This lets us use the unconfigured cameras to cover all auth cases for free.


@pytest.mark.parametrize(
    ("user_idx", "cam_id", "status_code", "status_detail"),
    [
        # No token
        (None, 1, 401, "Not authenticated"),
        # Camera does not exist
        (0, 999, 404, "Table Camera has no corresponding entry."),
        # Cross-org: agent org1 → cam-2 org2
        (1, 2, 403, "Access forbidden."),
        # Cross-org: user org2 → cam-1 org1
        (2, 1, 403, "Access forbidden."),
        # Correct scope + own org → no device config → 409
        (0, 1, 409, "Camera device connection is not configured"),
        (1, 1, 409, "Camera device connection is not configured"),
        (2, 2, 409, "Camera device connection is not configured"),
    ],
)
@pytest.mark.asyncio
async def test_proxy_read_auth(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    user_idx,
    cam_id,
    status_code,
    status_detail,
):
    auth = _auth(user_idx) if user_idx is not None else None
    response = await async_client.get(f"/cameras/{cam_id}/health", headers=auth)
    assert response.status_code == status_code
    if status_detail:
        assert status_detail in response.json()["detail"]


@pytest.mark.parametrize(
    ("user_idx", "cam_id", "status_code", "status_detail"),
    [
        # No token
        (None, 1, 401, "Not authenticated"),
        # USER role is not allowed on write endpoints
        (2, 2, 403, "Incompatible token scope."),
        # Cross-org: agent org1 → cam-2 org2
        (1, 2, 403, "Access forbidden."),
        # Correct scope + own org → no device config → 409
        (0, 1, 409, "Camera device connection is not configured"),
        (1, 1, 409, "Camera device connection is not configured"),
    ],
)
@pytest.mark.asyncio
async def test_proxy_write_auth(
    async_client: AsyncClient,
    camera_session: AsyncSession,
    user_idx,
    cam_id,
    status_code,
    status_detail,
):
    auth = _auth(user_idx) if user_idx is not None else None
    response = await async_client.post(f"/cameras/{cam_id}/control/move", headers=auth)
    assert response.status_code == status_code
    if status_detail:
        assert status_detail in response.json()["detail"]


# ── Device not configured → 409 on every route ───────────────────────────────


@pytest.mark.parametrize(
    "path",
    [
        "/cameras/1/health",
        "/cameras/1/cameras_list",
        "/cameras/1/camera_infos",
        "/cameras/1/capture",
        "/cameras/1/latest_image?pose=0",
        "/cameras/1/control/presets",
        "/cameras/1/control/speed_tables",
        "/cameras/1/focus/status",
        "/cameras/1/patrol/status",
        "/cameras/1/stream/status",
        "/cameras/1/stream/is_running",
    ],
)
@pytest.mark.asyncio
async def test_proxy_unconfigured_get(async_client: AsyncClient, camera_session: AsyncSession, path: str):
    response = await async_client.get(path, headers=_auth(0))
    assert response.status_code == 409
    assert "not configured" in response.json()["detail"]


@pytest.mark.parametrize(
    "path",
    [
        "/cameras/1/control/move",
        "/cameras/1/control/goto_preset?pose_id=1",
        "/cameras/1/control/start_move?direction=Left",
        "/cameras/1/control/stop_move",
        "/cameras/1/control/move_for_duration?direction=Left&duration=1",
        "/cameras/1/control/move_by_degrees?direction=Left&degrees=5",
        "/cameras/1/control/click_to_move?click_x=0.5&click_y=0.5",
        "/cameras/1/control/stop",
        "/cameras/1/control/preset",
        "/cameras/1/control/zoom/5",
        "/cameras/1/patrol/start",
        "/cameras/1/patrol/stop",
        "/cameras/1/stream/start",
        "/cameras/1/stream/stop",
        "/cameras/1/focus/manual?position=500",
        "/cameras/1/focus/autofocus",
        "/cameras/1/focus/optimize",
    ],
)
@pytest.mark.asyncio
async def test_proxy_unconfigured_post(async_client: AsyncClient, camera_session: AsyncSession, path: str):
    response = await async_client.post(path, headers=_auth(0))
    assert response.status_code == 409
    assert "not configured" in response.json()["detail"]


# ── Device error forwarding ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_proxy_device_timeout(async_client: AsyncClient, configured_camera_session: AsyncSession):
    with patch(
        f"{_PROXY_MODULE}._run_sync",
        side_effect=HTTPException(status_code=504, detail="Camera device is not responding."),
    ):
        response = await async_client.get(f"/cameras/{CONFIGURED_CAM_ID}/health", headers=_auth(0))
    assert response.status_code == 504
    assert "not responding" in response.json()["detail"]


@pytest.mark.asyncio
async def test_proxy_device_unreachable(async_client: AsyncClient, configured_camera_session: AsyncSession):
    with patch(
        f"{_PROXY_MODULE}._run_sync",
        side_effect=HTTPException(status_code=502, detail="Failed to reach camera device."),
    ):
        response = await async_client.get(f"/cameras/{CONFIGURED_CAM_ID}/health", headers=_auth(0))
    assert response.status_code == 502
    assert "reach camera device" in response.json()["detail"]


@pytest.mark.asyncio
async def test_proxy_device_error_forwarded(async_client: AsyncClient, configured_camera_session: AsyncSession):
    """A 404 from the device (unknown camera_ip) is forwarded as-is."""
    with patch(f"{_PROXY_MODULE}._run_sync", side_effect=HTTPException(status_code=404, detail="Unknown camera")):
        response = await async_client.get(f"/cameras/{CONFIGURED_CAM_ID}/health", headers=_auth(0))
    assert response.status_code == 404


# ── Binary (JPEG) responses ───────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_proxy_capture_returns_jpeg(async_client: AsyncClient, configured_camera_session: AsyncSession):
    with patch(f"{_PROXY_MODULE}._run_sync", new=AsyncMock(return_value=FAKE_JPEG)):
        response = await async_client.get(f"/cameras/{CONFIGURED_CAM_ID}/capture", headers=_auth(0))
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content == FAKE_JPEG


@pytest.mark.asyncio
async def test_proxy_latest_image_returns_jpeg(async_client: AsyncClient, configured_camera_session: AsyncSession):
    """The endpoint re-encodes the PIL Image returned by the client into JPEG bytes."""
    img = Image.new("RGB", (4, 4), color=(255, 0, 0))
    with patch(f"{_PROXY_MODULE}._run_sync", new=AsyncMock(return_value=img)):
        response = await async_client.get(f"/cameras/{CONFIGURED_CAM_ID}/latest_image?pose=0", headers=_auth(0))
    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"
    assert response.content[:2] == b"\xff\xd8"  # JPEG magic bytes


@pytest.mark.asyncio
async def test_proxy_latest_image_no_content(async_client: AsyncClient, configured_camera_session: AsyncSession):
    """When the device has no cached image for the requested pose it returns 204."""
    with patch(f"{_PROXY_MODULE}._run_sync", new=AsyncMock(return_value=None)):
        response = await async_client.get(f"/cameras/{CONFIGURED_CAM_ID}/latest_image?pose=0", headers=_auth(0))
    assert response.status_code == 204


# ── device_ip / camera_ip must never appear in API responses ─────────────────


@pytest.mark.asyncio
async def test_device_ip_not_leaked_in_camera_response(
    async_client: AsyncClient, configured_camera_session: AsyncSession, pose_session: AsyncSession
):
    """GET /cameras/{id} must not expose device_ip or camera_ip even for a configured camera."""
    response = await async_client.get(f"/cameras/{CONFIGURED_CAM_ID}", headers=_auth(0))
    assert response.status_code == 200
    data = response.json()
    assert "device_ip" not in data
    assert "camera_ip" not in data


# ── Happy-path coverage for all remaining proxy endpoints ────────────────────


@pytest.mark.parametrize(
    ("path", "method"),
    [
        (f"/cameras/{CONFIGURED_CAM_ID}/health", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/cameras_list", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/camera_infos", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/presets", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/speed_tables", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/focus/status", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/patrol/status", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/stream/status", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/stream/is_running", "get"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/move", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/goto_preset?pose_id=1", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/start_move?direction=Left", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/stop_move", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/move_for_duration?direction=Left&duration=1", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/move_by_degrees?direction=Left&degrees=5", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/click_to_move?click_x=0.5&click_y=0.5", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/stop", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/preset", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/control/zoom/5", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/focus/manual?position=500", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/focus/autofocus", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/focus/optimize", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/patrol/start", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/patrol/stop", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/stream/start", "post"),
        (f"/cameras/{CONFIGURED_CAM_ID}/stream/stop", "post"),
    ],
)
@pytest.mark.asyncio
async def test_proxy_happy_path(
    async_client: AsyncClient,
    configured_camera_session: AsyncSession,
    path: str,
    method: str,
):
    with patch(f"{_PROXY_MODULE}._run_sync", new=AsyncMock(return_value={"ok": True})):
        response = await getattr(async_client, method)(path, headers=_auth(0))
    assert response.status_code == 200
