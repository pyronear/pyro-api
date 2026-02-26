# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

"""HTTP client for the camera device API.

Base URL: http://{device_ip}:8081

camera_ip is the IP of the specific PTZ camera managed by the device. It is
passed as a path parameter when the swagger path contains {camera_ip}, or as
a query parameter otherwise. POST endpoints on the device API use query params
(not request body) for all their inputs.

Endpoints that return JPEG images (capture, get_latest_image) use raw=True and
return bytes instead of JSON. get_latest_image may return None when the device
responds with 204 (no cached image for the requested pose).

All functions raise FastAPI HTTPExceptions so they can be used directly in route handlers:
  - 504 if the device does not respond within TIMEOUT seconds
  - 502 if the device is unreachable (connection error)
  - the device's own status code for any other HTTP error
"""

from typing import Any

import httpx
from fastapi import HTTPException, status

__all__ = [
    "capture",
    "get_camera_infos",
    "get_focus_status",
    "get_health",
    "get_latest_image",
    "get_patrol_status",
    "get_stream_status",
    "is_stream_running",
    "list_cameras",
    "list_presets",
    "manual_focus",
    "move",
    "run_focus_finder",
    "set_autofocus",
    "set_preset",
    "start_patrol",
    "start_stream",
    "stop",
    "stop_patrol",
    "stop_stream",
    "zoom",
]

DEVICE_PORT = 8081
TIMEOUT = 10.0


async def _request(
    method: str,
    device_ip: str,
    path: str,
    json: Any = None,
    params: dict[str, Any] | None = None,
    raw: bool = False,
) -> Any:
    url = f"http://{device_ip}:{DEVICE_PORT}{path}"
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        try:
            response = await client.request(method, url, json=json, params=params)
            if response.status_code == status.HTTP_204_NO_CONTENT:
                return None
            response.raise_for_status()
            return response.content if raw else response.json()
        except httpx.TimeoutException:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail="Camera device is not responding.",
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=exc.response.status_code,
                detail=exc.response.text,
            )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Failed to reach camera device.",
            )


# ── Health ────────────────────────────────────────────────────────────────────


async def get_health(device_ip: str) -> Any:
    return await _request("GET", device_ip, "/health")


# ── Cameras ───────────────────────────────────────────────────────────────────


async def list_cameras(device_ip: str) -> Any:
    """List all cameras managed by the device."""
    return await _request("GET", device_ip, "/cameras/cameras_list")


async def get_camera_infos(device_ip: str) -> Any:
    """Return metadata for all configured cameras on the device (no camera_ip filter)."""
    return await _request("GET", device_ip, "/cameras/camera_infos")


async def capture(
    device_ip: str,
    camera_ip: str,
    *,
    pos_id: int | None = None,
    anonymize: bool = True,
    max_age_ms: int | None = None,
    strict: bool = False,
    width: int | None = None,
    quality: int = 95,
) -> bytes | None:
    """Capture a JPEG snapshot. Returns raw bytes."""
    params: dict[str, Any] = {
        "camera_ip": camera_ip,
        "anonymize": anonymize,
        "strict": strict,
        "quality": quality,
    }
    if pos_id is not None:
        params["pos_id"] = pos_id
    if max_age_ms is not None:
        params["max_age_ms"] = max_age_ms
    if width is not None:
        params["width"] = width
    return await _request("GET", device_ip, "/cameras/capture", params=params, raw=True)


async def get_latest_image(
    device_ip: str,
    camera_ip: str,
    pose: int,
    quality: int = 95,
) -> bytes | None:
    """Return the last stored JPEG for a given pose. Returns None if no image (204)."""
    return await _request(
        "GET",
        device_ip,
        "/cameras/latest_image",
        params={"camera_ip": camera_ip, "pose": pose, "quality": quality},
        raw=True,
    )


# ── Control ───────────────────────────────────────────────────────────────────


async def move(
    device_ip: str,
    camera_ip: str,
    direction: str | None = None,
    speed: int = 10,
    pose_id: int | None = None,
    degrees: float | None = None,
) -> Any:
    params: dict[str, Any] = {"camera_ip": camera_ip, "speed": speed}
    if direction is not None:
        params["direction"] = direction
    if pose_id is not None:
        params["pose_id"] = pose_id
    if degrees is not None:
        params["degrees"] = degrees
    return await _request("POST", device_ip, "/control/move", params=params)


async def stop(device_ip: str, camera_ip: str) -> Any:
    return await _request("POST", device_ip, f"/control/stop/{camera_ip}")


async def list_presets(device_ip: str, camera_ip: str) -> Any:
    return await _request("GET", device_ip, "/control/preset/list", params={"camera_ip": camera_ip})


async def set_preset(device_ip: str, camera_ip: str, idx: int | None = None) -> Any:
    params: dict[str, Any] = {"camera_ip": camera_ip}
    if idx is not None:
        params["idx"] = idx
    return await _request("POST", device_ip, "/control/preset/set", params=params)


async def zoom(device_ip: str, camera_ip: str, level: int) -> Any:
    return await _request("POST", device_ip, f"/control/zoom/{camera_ip}/{level}")


# ── Focus ─────────────────────────────────────────────────────────────────────


async def manual_focus(device_ip: str, camera_ip: str, position: int) -> Any:
    return await _request("POST", device_ip, "/focus/manual", params={"camera_ip": camera_ip, "position": position})


async def set_autofocus(device_ip: str, camera_ip: str, disable: bool = True) -> Any:
    return await _request(
        "POST", device_ip, "/focus/set_autofocus", params={"camera_ip": camera_ip, "disable": disable}
    )


async def get_focus_status(device_ip: str, camera_ip: str) -> Any:
    return await _request("GET", device_ip, "/focus/status", params={"camera_ip": camera_ip})


async def run_focus_finder(device_ip: str, camera_ip: str, save_images: bool = False) -> Any:
    return await _request(
        "POST", device_ip, "/focus/focus_finder", params={"camera_ip": camera_ip, "save_images": save_images}
    )


# ── Patrol ────────────────────────────────────────────────────────────────────


async def start_patrol(device_ip: str, camera_ip: str) -> Any:
    return await _request("POST", device_ip, "/patrol/start_patrol", params={"camera_ip": camera_ip})


async def stop_patrol(device_ip: str, camera_ip: str) -> Any:
    return await _request("POST", device_ip, "/patrol/stop_patrol", params={"camera_ip": camera_ip})


async def get_patrol_status(device_ip: str, camera_ip: str) -> Any:
    return await _request("GET", device_ip, "/patrol/patrol_status", params={"camera_ip": camera_ip})


# ── Stream ────────────────────────────────────────────────────────────────────


async def start_stream(device_ip: str, camera_ip: str) -> Any:
    return await _request("POST", device_ip, f"/stream/start_stream/{camera_ip}")


async def stop_stream(device_ip: str) -> Any:
    """Stop whatever stream is currently running on the device (device-global, no camera_ip)."""
    return await _request("POST", device_ip, "/stream/stop_stream")


async def get_stream_status(device_ip: str) -> Any:
    """Return the stream status for the device (device-global, no camera_ip)."""
    return await _request("GET", device_ip, "/stream/status")


async def is_stream_running(device_ip: str, camera_ip: str) -> Any:
    return await _request("GET", device_ip, f"/stream/is_stream_running/{camera_ip}")
