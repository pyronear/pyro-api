from contextlib import contextmanager
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest
from fastapi import HTTPException

from app.services import camera_client

DEVICE_IP = "192.168.1.100"
CAMERA_IP = "192.168.1.101"
FAKE_JPEG = b"\xff\xd8\xff" + b"\x00" * 16


@contextmanager
def _mock_httpx(*, status_code: int = 200, json_body=None, content: bytes = b"", side_effect=None, raise_status=None):
    """Patch httpx.AsyncClient so _request never opens a real connection."""
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json_body if json_body is not None else {}
    mock_response.content = content
    if raise_status is not None:
        mock_response.raise_for_status.side_effect = raise_status
    else:
        mock_response.raise_for_status = MagicMock()

    mock_http = AsyncMock()
    mock_http.request = (
        AsyncMock(side_effect=side_effect) if side_effect is not None else AsyncMock(return_value=mock_response)
    )

    mock_instance = MagicMock()
    mock_instance.__aenter__ = AsyncMock(return_value=mock_http)
    mock_instance.__aexit__ = AsyncMock(return_value=False)

    with patch("app.services.camera_client.httpx.AsyncClient", return_value=mock_instance):
        yield mock_http


# ── _request error paths ──────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_request_timeout():
    with _mock_httpx(side_effect=httpx.TimeoutException("")), pytest.raises(HTTPException) as exc_info:
        await camera_client.get_health(DEVICE_IP)
    assert exc_info.value.status_code == 504
    assert "not responding" in exc_info.value.detail


@pytest.mark.asyncio
async def test_request_connection_error():
    with _mock_httpx(side_effect=httpx.ConnectError("")), pytest.raises(HTTPException) as exc_info:
        await camera_client.get_health(DEVICE_IP)
    assert exc_info.value.status_code == 502
    assert "reach camera device" in exc_info.value.detail


@pytest.mark.asyncio
async def test_request_http_status_forwarded():
    err_resp = MagicMock()
    err_resp.status_code = 404
    err_resp.text = "Unknown camera"
    with (
        _mock_httpx(raise_status=httpx.HTTPStatusError("", request=MagicMock(), response=err_resp)),
        pytest.raises(HTTPException) as exc_info,
    ):
        await camera_client.get_health(DEVICE_IP)
    assert exc_info.value.status_code == 404
    assert "Unknown camera" in exc_info.value.detail


@pytest.mark.asyncio
async def test_request_204_returns_none():
    with _mock_httpx(status_code=204):
        result = await camera_client.get_latest_image(DEVICE_IP, CAMERA_IP, pose=0)
    assert result is None


@pytest.mark.asyncio
async def test_request_raw_returns_bytes():
    with _mock_httpx(content=FAKE_JPEG):
        result = await camera_client.capture(DEVICE_IP, CAMERA_IP)
    assert result == FAKE_JPEG


@pytest.mark.asyncio
async def test_capture_optional_params():
    """Covers the pos_id / max_age_ms / width conditional branches in capture()."""
    with _mock_httpx(content=FAKE_JPEG):
        result = await camera_client.capture(DEVICE_IP, CAMERA_IP, pos_id=1, max_age_ms=200, width=640)
    assert result == FAKE_JPEG


# ── Individual client functions ───────────────────────────────────────────────


@pytest.mark.parametrize(
    ("func", "args", "kwargs"),
    [
        (camera_client.get_health, (DEVICE_IP,), {}),
        (camera_client.list_cameras, (DEVICE_IP,), {}),
        (camera_client.get_camera_infos, (DEVICE_IP,), {}),
        # move: no optional params
        (camera_client.move, (DEVICE_IP, CAMERA_IP), {}),
        # move: all optional params (covers direction / pose_id / degrees branches)
        (camera_client.move, (DEVICE_IP, CAMERA_IP), {"direction": "Left", "pose_id": 1, "degrees": 45.0}),
        (camera_client.stop, (DEVICE_IP, CAMERA_IP), {}),
        (camera_client.list_presets, (DEVICE_IP, CAMERA_IP), {}),
        # set_preset: without idx (None branch)
        (camera_client.set_preset, (DEVICE_IP, CAMERA_IP), {}),
        # set_preset: with idx
        (camera_client.set_preset, (DEVICE_IP, CAMERA_IP), {"idx": 2}),
        (camera_client.zoom, (DEVICE_IP, CAMERA_IP, 10), {}),
        (camera_client.manual_focus, (DEVICE_IP, CAMERA_IP, 500), {}),
        (camera_client.set_autofocus, (DEVICE_IP, CAMERA_IP), {}),
        (camera_client.get_focus_status, (DEVICE_IP, CAMERA_IP), {}),
        (camera_client.run_focus_finder, (DEVICE_IP, CAMERA_IP), {}),
        (camera_client.run_focus_finder, (DEVICE_IP, CAMERA_IP), {"save_images": True}),
        (camera_client.start_patrol, (DEVICE_IP, CAMERA_IP), {}),
        (camera_client.stop_patrol, (DEVICE_IP, CAMERA_IP), {}),
        (camera_client.get_patrol_status, (DEVICE_IP, CAMERA_IP), {}),
        (camera_client.start_stream, (DEVICE_IP, CAMERA_IP), {}),
        (camera_client.stop_stream, (DEVICE_IP,), {}),
        (camera_client.get_stream_status, (DEVICE_IP,), {}),
        (camera_client.is_stream_running, (DEVICE_IP, CAMERA_IP), {}),
    ],
)
@pytest.mark.asyncio
async def test_client_function_success(func, args, kwargs):
    with _mock_httpx(json_body={"ok": True}):
        result = await func(*args, **kwargs)
    assert result == {"ok": True}
