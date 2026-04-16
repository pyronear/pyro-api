# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


import asyncio
import io
from collections.abc import Callable
from functools import partial
from typing import Any, cast

import requests
from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, Security, status
from pyro_camera_api_client import PyroCameraAPIClient

from app.api.dependencies import get_camera_crud, get_jwt
from app.crud import CameraCRUD
from app.models import Camera, UserRole
from app.schemas.login import TokenPayload

router = APIRouter()

DEVICE_PORT = 8081
TIMEOUT = 10.0


def _make_client(device_ip: str) -> PyroCameraAPIClient:
    return PyroCameraAPIClient(base_url=f"http://{device_ip}:{DEVICE_PORT}", timeout=TIMEOUT)


async def _run_sync(fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
    loop = asyncio.get_running_loop()
    try:
        return await loop.run_in_executor(None, partial(fn, *args, **kwargs))
    except requests.exceptions.Timeout:
        raise HTTPException(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            detail="Camera device is not responding.",
        )
    except requests.exceptions.HTTPError as exc:
        raise HTTPException(
            status_code=exc.response.status_code,
            detail=exc.response.text,
        )
    except requests.exceptions.ConnectionError:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Failed to reach camera device.",
        )


# ── Shared helpers ────────────────────────────────────────────────────────────


async def _require_read(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Camera:
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return camera


async def _require_write(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> Camera:
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return camera


def _device_config(camera: Camera) -> tuple[str, str]:
    """Return (device_ip, camera_ip) or raise 409 if the camera is not configured."""
    if not camera.device_ip or not camera.camera_ip:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Camera device connection is not configured (missing device_ip or camera_ip).",
        )
    return camera.device_ip, camera.camera_ip


# ── Health ────────────────────────────────────────────────────────────────────


@router.get("/{camera_id}/health", status_code=status.HTTP_200_OK, summary="Camera device health check")
async def proxy_health(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, _ = _device_config(camera)
    return await _run_sync(_make_client(device_ip).health)


# ── Device cameras ────────────────────────────────────────────────────────────


@router.get("/{camera_id}/cameras_list", status_code=status.HTTP_200_OK, summary="List all cameras on the device")
async def proxy_cameras_list(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, _ = _device_config(camera)
    return await _run_sync(_make_client(device_ip).list_cameras)


@router.get("/{camera_id}/camera_infos", status_code=status.HTTP_200_OK, summary="Get all camera infos from the device")
async def proxy_camera_infos(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, _ = _device_config(camera)
    return await _run_sync(_make_client(device_ip).get_camera_infos)


@router.get("/{camera_id}/capture", status_code=status.HTTP_200_OK, summary="Capture a JPEG snapshot from the camera")
async def proxy_capture(
    patrol_id: int | None = Query(default=None, description="Move to this preset pose before capturing"),
    anonymize: bool = Query(default=True, description="Overlay anonymization masks on the image"),
    max_age_ms: int | None = Query(default=None, description="Only use detection boxes newer than this many ms"),
    strict: bool = Query(default=False, description="Return 503 if no recent boxes are available for anonymization"),
    width: int | None = Query(default=None, description="Resize output to this width (px), preserving aspect ratio"),
    quality: int = Query(default=95, ge=1, le=100, description="JPEG quality (1-100)"),
    camera: Camera = Depends(_require_read),
) -> Response:
    device_ip, camera_ip = _device_config(camera)
    data = await _run_sync(
        _make_client(device_ip).capture_jpeg,
        camera_ip,
        patrol_id=patrol_id,
        anonymize=anonymize,
        max_age_ms=max_age_ms,
        strict=strict,
        width=width,
        quality=quality,
    )
    return Response(content=data, media_type="image/jpeg")


@router.get("/{camera_id}/latest_image", status_code=status.HTTP_200_OK, summary="Get the last stored image for a pose")
async def proxy_latest_image(
    pose: int = Query(..., description="Pose index whose cached image to retrieve"),
    quality: int = Query(default=95, ge=1, le=100, description="JPEG quality (1-100)"),
    camera: Camera = Depends(_require_read),
) -> Response:
    device_ip, camera_ip = _device_config(camera)
    image = await _run_sync(_make_client(device_ip).get_latest_image, camera_ip, pose, quality)
    if image is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    return Response(content=buf.getvalue(), media_type="image/jpeg")


# ── Control ───────────────────────────────────────────────────────────────────


@router.post("/{camera_id}/control/move", status_code=status.HTTP_200_OK, summary="Move the camera (legacy)")
async def proxy_move(
    direction: str | None = Query(default=None, description="Direction: Left, Right, Up, Down"),
    speed: int = Query(default=10, description="Movement speed"),
    pose_id: int | None = Query(default=None, description="Move to this preset pose index"),
    degrees: float | None = Query(default=None, description="Rotate by this many degrees (requires direction)"),
    duration: float | None = Query(default=None, description="Move for this many seconds (requires direction)"),
    zoom: int = Query(default=0, description="Zoom level; speed is forced to 1 server-side when zoom > 0"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(
        _make_client(device_ip).move_camera,
        camera_ip,
        direction=direction,
        speed=speed,
        pose_id=pose_id,
        degrees=degrees,
        duration=duration,
        zoom=zoom,
    )


@router.post("/{camera_id}/control/goto_preset", status_code=status.HTTP_200_OK, summary="Move to a preset pose")
async def proxy_goto_preset(
    pose_id: int = Query(..., description="Preset pose index to move to"),
    speed: int = Query(default=50, description="Movement speed"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).goto_preset, camera_ip, pose_id, speed)


@router.post("/{camera_id}/control/start_move", status_code=status.HTTP_200_OK, summary="Start a continuous move")
async def proxy_start_move(
    direction: str = Query(..., description="Direction: Left, Right, Up, Down"),
    speed: int = Query(default=10, description="Movement speed"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).start_move, camera_ip, direction, speed)


@router.post("/{camera_id}/control/stop_move", status_code=status.HTTP_200_OK, summary="Halt current movement")
async def proxy_stop_move(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).stop_move, camera_ip)


@router.post(
    "/{camera_id}/control/move_for_duration",
    status_code=status.HTTP_200_OK,
    summary="Move for a fixed duration (seconds)",
)
async def proxy_move_for_duration(
    direction: str = Query(..., description="Direction: Left, Right, Up, Down"),
    duration: float = Query(..., gt=0, description="Movement duration in seconds"),
    speed: int = Query(default=10, description="Movement speed"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(
        _make_client(device_ip).move_for_duration,
        camera_ip,
        direction,
        duration,
        speed,
    )


@router.post(
    "/{camera_id}/control/move_by_degrees",
    status_code=status.HTTP_200_OK,
    summary="Move by an approximate angle",
)
async def proxy_move_by_degrees(
    direction: str = Query(..., description="Direction: Left, Right, Up, Down"),
    degrees: float = Query(..., gt=0, description="Approximate rotation in degrees"),
    speed: int = Query(default=10, description="Movement speed"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(
        _make_client(device_ip).move_by_degrees,
        camera_ip,
        direction,
        degrees,
        speed,
    )


@router.post(
    "/{camera_id}/control/click_to_move",
    status_code=status.HTTP_200_OK,
    summary="Move toward a normalized image click",
)
async def proxy_click_to_move(
    click_x: float = Query(..., ge=0.0, le=1.0, description="Normalized x coordinate in [0, 1]"),
    click_y: float = Query(..., ge=0.0, le=1.0, description="Normalized y coordinate in [0, 1]"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(
        _make_client(device_ip).click_to_move,
        camera_ip,
        click_x,
        click_y,
    )


@router.get(
    "/{camera_id}/control/speed_tables",
    status_code=status.HTTP_200_OK,
    summary="Get calibrated speed tables",
)
async def proxy_speed_tables(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).get_speed_tables, camera_ip)


@router.post("/{camera_id}/control/stop", status_code=status.HTTP_200_OK, summary="Stop the camera")
async def proxy_stop(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).stop_camera, camera_ip)


@router.get("/{camera_id}/control/presets", status_code=status.HTTP_200_OK, summary="List available presets")
async def proxy_list_presets(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).list_presets, camera_ip)


@router.post("/{camera_id}/control/preset", status_code=status.HTTP_200_OK, summary="Set a preset position")
async def proxy_set_preset(
    idx: int | None = Query(
        default=None, description="Preset slot index to write (adapter picks free slot if omitted)"
    ),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).set_preset, camera_ip, idx=idx)


@router.post("/{camera_id}/control/zoom/{level}", status_code=status.HTTP_200_OK, summary="Zoom the camera")
async def proxy_zoom(
    level: int = Path(..., ge=0, le=64, description="Zoom level (0-64)"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).zoom, camera_ip, level)


# ── Focus ─────────────────────────────────────────────────────────────────────


@router.post("/{camera_id}/focus/manual", status_code=status.HTTP_200_OK, summary="Set manual focus position")
async def proxy_manual_focus(
    position: int = Query(..., description="Focus motor position (0-1000)"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).set_manual_focus, camera_ip, position)


@router.post("/{camera_id}/focus/autofocus", status_code=status.HTTP_200_OK, summary="Toggle autofocus")
async def proxy_set_autofocus(
    disable: bool = Query(default=True, description="True to disable autofocus (enable manual), False to re-enable it"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).set_autofocus, camera_ip, disable)


@router.get("/{camera_id}/focus/status", status_code=status.HTTP_200_OK, summary="Get focus status")
async def proxy_focus_status(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).get_focus_status, camera_ip)


@router.post("/{camera_id}/focus/optimize", status_code=status.HTTP_200_OK, summary="Run focus optimization")
async def proxy_focus_finder(
    save_images: bool = Query(default=False, description="Save intermediate frames captured during focus search"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).run_focus_optimization, camera_ip, save_images=save_images)


# ── Patrol ────────────────────────────────────────────────────────────────────


@router.post("/{camera_id}/patrol/start", status_code=status.HTTP_200_OK, summary="Start patrol")
async def proxy_start_patrol(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).start_patrol, camera_ip)


@router.post("/{camera_id}/patrol/stop", status_code=status.HTTP_200_OK, summary="Stop patrol")
async def proxy_stop_patrol(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).stop_patrol, camera_ip)


@router.get("/{camera_id}/patrol/status", status_code=status.HTTP_200_OK, summary="Get patrol status")
async def proxy_patrol_status(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).get_patrol_status, camera_ip)


# ── Stream ────────────────────────────────────────────────────────────────────


@router.post("/{camera_id}/stream/start", status_code=status.HTTP_200_OK, summary="Start video stream")
async def proxy_start_stream(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).start_stream, camera_ip)


@router.post("/{camera_id}/stream/stop", status_code=status.HTTP_200_OK, summary="Stop video stream")
async def proxy_stop_stream(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, _ = _device_config(camera)
    return await _run_sync(_make_client(device_ip).stop_stream)


@router.get("/{camera_id}/stream/status", status_code=status.HTTP_200_OK, summary="Get stream status")
async def proxy_stream_status(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, _ = _device_config(camera)
    return await _run_sync(_make_client(device_ip).get_stream_status)


@router.get("/{camera_id}/stream/is_running", status_code=status.HTTP_200_OK, summary="Check if stream is running")
async def proxy_is_stream_running(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await _run_sync(_make_client(device_ip).is_stream_running, camera_ip)
