# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import logging
from datetime import date
from typing import Union

import httpx

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

__all__ = ["risk_service", "min_confidence_for_class"]

# EFFIS classes that should trigger filtering. Anything else (moderate+) → no filter.
_LOW = "low"
_VERY_LOW = "very_low"


def min_confidence_for_class(fwi_class: Union[str, None]) -> Union[float, None]:
    """Return the min confidence required for this FWI class, or None if no filter applies."""
    if fwi_class == _VERY_LOW:
        return settings.FWI_VERY_LOW_MIN_CONF
    if fwi_class == _LOW:
        return settings.FWI_LOW_MIN_CONF
    return None


class RiskService:
    """In-memory cache of the daily FWI class per camera.

    Refreshed once at startup and once a day from the pyro-risk-api service.
    Fail-open: if the API is unreachable or a camera is unknown, no filter is applied.
    """

    def __init__(self) -> None:
        self._scores: dict[int, str] = {}

    @property
    def is_configured(self) -> bool:
        return bool(settings.RISK_API_HOST and settings.RISK_API_USERNAME and settings.RISK_API_PASSWORD)

    def min_confidence(self, camera_id: int) -> Union[float, None]:
        """Return the min confidence required for this camera (today), or None if no filter."""
        return min_confidence_for_class(self._scores.get(camera_id))

    async def _fetch(self, path: str, params: Union[dict, None] = None) -> Union[list, dict, None]:
        if not self.is_configured:
            return None
        host = settings.RISK_API_HOST.rstrip("/")  # type: ignore[union-attr]
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{host}/{path.lstrip('/')}",
                    params=params,
                    auth=(settings.RISK_API_USERNAME, settings.RISK_API_PASSWORD),  # type: ignore[arg-type]
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Risk API call %s failed (%s)", path, exc)
            return None

    async def refresh(self) -> None:
        """Fetch fresh FWI classes from the risk API. On error, keep the previous cache."""
        payload = await self._fetch("cameras")
        if not isinstance(payload, list):
            logger.warning("Risk API refresh: keeping previous cache (%d entries)", len(self._scores))
            return

        scores: dict[int, str] = {}
        for item in payload:
            camera_id = item.get("id")
            fwi_class = item.get("fwi_class")
            if isinstance(camera_id, int) and isinstance(fwi_class, str):
                scores[camera_id] = fwi_class
        self._scores = scores
        logger.info("Risk API refresh: cached FWI class for %d camera(s)", len(scores))

    async def get_scores_for_date(self, target_date: date) -> dict[int, str]:
        """Fetch persisted FWI classes for a specific date. Returns {} on error or when not configured."""
        payload = await self._fetch(f"scores/{target_date.isoformat()}")
        if not isinstance(payload, list):
            return {}
        scores: dict[int, str] = {}
        for item in payload:
            camera_id = item.get("id") or item.get("camera_id")
            fwi_class = item.get("fwi_class")
            if isinstance(camera_id, int) and isinstance(fwi_class, str):
                scores[camera_id] = fwi_class
        return scores


risk_service = RiskService()
