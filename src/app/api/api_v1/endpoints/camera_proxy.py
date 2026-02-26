# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Path, Query, Response, Security, status

from app.api.dependencies import get_camera_crud, get_jwt
from app.crud import CameraCRUD
from app.models import Camera, UserRole
from app.schemas.login import TokenPayload
from app.services import camera_client

router = APIRouter()


# ── Shared helpers ────────────────────────────────────────────────────────────


async def _require_read(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(
        get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT, UserRole.USER]),
) -> Camera:
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
    return camera


async def _require_write(
    camera_id: int = Path(..., gt=0),
    cameras: CameraCRUD = Depends(get_camera_crud),
    token_payload: TokenPayload = Security(
        get_jwt, scopes=[UserRole.ADMIN, UserRole.AGENT]),
) -> Camera:
    camera = cast(Camera, await cameras.get(camera_id, strict=True))
    if token_payload.organization_id != camera.organization_id and UserRole.ADMIN not in token_payload.scopes:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access forbidden.")
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
    return await camera_client.get_health(device_ip)


# ── Device cameras ────────────────────────────────────────────────────────────


@router.get("/{camera_id}/cameras_list", status_code=status.HTTP_200_OK, summary="List all cameras on the device")
async def proxy_cameras_list(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, _ = _device_config(camera)
    return await camera_client.list_cameras(device_ip)


@router.get("/{camera_id}/camera_infos", status_code=status.HTTP_200_OK, summary="Get all camera infos from the device")
async def proxy_camera_infos(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, _ = _device_config(camera)
    return await camera_client.get_camera_infos(device_ip)


@router.get("/{camera_id}/capture", status_code=status.HTTP_200_OK, summary="Capture a JPEG snapshot from the camera")
async def proxy_capture(
    pos_id: int | None = Query(
        default=None, description="Move to this preset pose before capturing"),
    anonymize: bool = Query(
        default=True, description="Overlay anonymization masks on the image"),
    max_age_ms: int | None = Query(
        default=None, description="Only use detection boxes newer than this many ms"),
    strict: bool = Query(
        default=False, description="Return 503 if no recent boxes are available for anonymization"),
    width: int | None = Query(
        default=None, description="Resize output to this width (px), preserving aspect ratio"),
    quality: int = Query(default=95, ge=1, le=100,
                         description="JPEG quality (1–100)"),
    camera: Camera = Depends(_require_read),
) -> Response:
    device_ip, camera_ip = _device_config(camera)
    data = await camera_client.capture(
        device_ip,
        camera_ip,
        pos_id=pos_id,
        anonymize=anonymize,
        max_age_ms=max_age_ms,
        strict=strict,
        width=width,
        quality=quality,
    )
    return Response(content=data, media_type="image/jpeg")


@router.get("/{camera_id}/latest_image", status_code=status.HTTP_200_OK, summary="Get the last stored image for a pose")
async def proxy_latest_image(
    pose: int = Query(...,
                      description="Pose index whose cached image to retrieve"),
    quality: int = Query(default=95, ge=1, le=100,
                         description="JPEG quality (1–100)"),
    camera: Camera = Depends(_require_read),
) -> Response:
    device_ip, camera_ip = _device_config(camera)
    data = await camera_client.get_latest_image(device_ip, camera_ip, pose, quality)
    if data is None:
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    return Response(content=data, media_type="image/jpeg")


# ── Control ───────────────────────────────────────────────────────────────────


@router.post("/{camera_id}/control/move", status_code=status.HTTP_200_OK, summary="Move the camera")
async def proxy_move(
    direction: str | None = Query(
        default=None, description="Direction: Left, Right, Up, Down"),
    speed: int = Query(default=10, description="Movement speed"),
    pose_id: int | None = Query(
        default=None, description="Move to this preset pose index"),
    degrees: float | None = Query(
        default=None, description="Rotate by this many degrees (requires direction)"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.move(
        device_ip, camera_ip, direction=direction, speed=speed, pose_id=pose_id, degrees=degrees
    )


@router.post("/{camera_id}/control/stop", status_code=status.HTTP_200_OK, summary="Stop camera movement")
async def proxy_stop(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.stop(device_ip, camera_ip)


@router.get("/{camera_id}/control/presets", status_code=status.HTTP_200_OK, summary="List available presets")
async def proxy_list_presets(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.list_presets(device_ip, camera_ip)


@router.post("/{camera_id}/control/preset", status_code=status.HTTP_200_OK, summary="Set a preset position")
async def proxy_set_preset(
    idx: int | None = Query(
        default=None, description="Preset slot index to write (adapter picks free slot if omitted)"
    ),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.set_preset(device_ip, camera_ip, idx=idx)


@router.post("/{camera_id}/control/zoom/{level}", status_code=status.HTTP_200_OK, summary="Zoom the camera")
async def proxy_zoom(
    level: int = Path(..., ge=0, le=64, description="Zoom level (0–64)"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.zoom(device_ip, camera_ip, level)


# ── Focus ─────────────────────────────────────────────────────────────────────


@router.post("/{camera_id}/focus/manual", status_code=status.HTTP_200_OK, summary="Set manual focus position")
async def proxy_manual_focus(
    position: int = Query(..., description="Focus motor position (0–1000)"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.manual_focus(device_ip, camera_ip, position)


@router.post("/{camera_id}/focus/autofocus", status_code=status.HTTP_200_OK, summary="Toggle autofocus")
async def proxy_set_autofocus(
    disable: bool = Query(
        default=True, description="True to disable autofocus (enable manual), False to re-enable it"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.set_autofocus(device_ip, camera_ip, disable)


@router.get("/{camera_id}/focus/status", status_code=status.HTTP_200_OK, summary="Get focus status")
async def proxy_focus_status(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.get_focus_status(device_ip, camera_ip)


@router.post("/{camera_id}/focus/optimize", status_code=status.HTTP_200_OK, summary="Run focus optimization")
async def proxy_focus_finder(
    save_images: bool = Query(
        default=False, description="Save intermediate frames captured during focus search"),
    camera: Camera = Depends(_require_write),
) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.run_focus_finder(device_ip, camera_ip, save_images)


# ── Patrol ────────────────────────────────────────────────────────────────────


@router.post("/{camera_id}/patrol/start", status_code=status.HTTP_200_OK, summary="Start patrol")
async def proxy_start_patrol(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.start_patrol(device_ip, camera_ip)


@router.post("/{camera_id}/patrol/stop", status_code=status.HTTP_200_OK, summary="Stop patrol")
async def proxy_stop_patrol(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.stop_patrol(device_ip, camera_ip)


@router.get("/{camera_id}/patrol/status", status_code=status.HTTP_200_OK, summary="Get patrol status")
async def proxy_patrol_status(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.get_patrol_status(device_ip, camera_ip)


# ── Stream ────────────────────────────────────────────────────────────────────


@router.post("/{camera_id}/stream/start", status_code=status.HTTP_200_OK, summary="Start video stream")
async def proxy_start_stream(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.start_stream(device_ip, camera_ip)


@router.post("/{camera_id}/stream/stop", status_code=status.HTTP_200_OK, summary="Stop video stream")
async def proxy_stop_stream(camera: Camera = Depends(_require_write)) -> Any:
    device_ip, _ = _device_config(camera)
    return await camera_client.stop_stream(device_ip)


@router.get("/{camera_id}/stream/status", status_code=status.HTTP_200_OK, summary="Get stream status")
async def proxy_stream_status(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, _ = _device_config(camera)
    return await camera_client.get_stream_status(device_ip)


@router.get("/{camera_id}/stream/is_running", status_code=status.HTTP_200_OK, summary="Check if stream is running")
async def proxy_is_stream_running(camera: Camera = Depends(_require_read)) -> Any:
    device_ip, camera_ip = _device_config(camera)
    return await camera_client.is_stream_running(device_ip, camera_ip)
