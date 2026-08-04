# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import logging
from math import isfinite
from typing import Any, NamedTuple
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

import httpx
from fastapi.encoders import jsonable_encoder

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")


class InferenceUnavailableError(RuntimeError):
    """Raised when the internal inference service cannot produce a valid result."""


class InferenceGroup(NamedTuple):
    sequence_ids: tuple[int, ...]
    smoke_location: tuple[float, float] | None


def _parse_groups(data: object) -> list[InferenceGroup]:
    if not isinstance(data, dict):
        raise ValueError("missing groups")
    items = data.get("groups")
    if not isinstance(items, list):
        raise ValueError("missing groups")
    groups: list[InferenceGroup] = []
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("invalid group")
        sequence_ids = item.get("sequence_ids")
        if not isinstance(sequence_ids, list):
            raise ValueError("invalid group")
        parsed_ids: list[int] = []
        for sequence_id in sequence_ids:
            if not isinstance(sequence_id, int) or isinstance(sequence_id, bool):
                raise ValueError("invalid sequence ids")
            parsed_ids.append(sequence_id)
        if not parsed_ids:
            raise ValueError("invalid sequence ids")
        if parsed_ids != sorted(set(parsed_ids)):
            raise ValueError("sequence ids are not canonical")
        location = item.get("smoke_location")
        smoke_location = None
        if location is not None:
            if not isinstance(location, dict):
                raise ValueError("invalid smoke location")
            lat = location.get("lat")
            lon = location.get("lon")
            if (
                not isinstance(lat, (int, float))
                or not isinstance(lon, (int, float))
                or not isfinite(lat)
                or not isfinite(lon)
                or not -90 <= lat <= 90
                or not -180 <= lon <= 180
            ):
                raise ValueError("invalid smoke location")
            smoke_location = float(lat), float(lon)
        groups.append(InferenceGroup(tuple(parsed_ids), smoke_location))
    return groups


class InferenceService:
    async def _post(self, path: str, payload: dict[str, Any]) -> object:
        if not settings.INFERENCE_API_URL or not settings.INFERENCE_API_TOKEN:
            raise InferenceUnavailableError("Inference API is not configured")
        host = settings.INFERENCE_API_URL.rstrip("/")
        headers = {"Authorization": f"Bearer {settings.INFERENCE_API_TOKEN}"}
        try:
            async with httpx.AsyncClient(timeout=settings.INFERENCE_API_TIMEOUT) as client:
                response = await client.post(f"{host}{path}", json=jsonable_encoder(payload), headers=headers)
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Inference API call to %s failed: %r", path, exc)
            raise InferenceUnavailableError(str(exc)) from exc

    async def triangulate(self, sequences: list[dict[str, Any]]) -> list[InferenceGroup]:
        try:
            return _parse_groups(await self._post("/v1/triangulate", {"sequences": sequences}))
        except ValueError as exc:
            logger.warning("Inference API returned an invalid triangulation response: %s", exc)
            raise InferenceUnavailableError(str(exc)) from exc

    async def timezone(self, lat: float, lon: float) -> str:
        data = await self._post("/v1/timezone", {"lat": lat, "lon": lon})
        timezone = data.get("timezone") if isinstance(data, dict) else None
        if not isinstance(timezone, str) or not timezone:
            raise InferenceUnavailableError("Inference API returned an invalid timezone response")
        try:
            ZoneInfo(timezone)
        except (ValueError, ZoneInfoNotFoundError) as exc:
            raise InferenceUnavailableError("Inference API returned an invalid timezone response") from exc
        return timezone


inference_service = InferenceService()
