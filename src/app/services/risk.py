# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import logging
from typing import Union

import httpx

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

__all__ = ["risk_service"]

# EFFIS classes that should trigger filtering. Anything else (moderate+) → no filter.
_LOW = "low"
_VERY_LOW = "very_low"


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
        """Return the min confidence required for this camera, or None if no filter applies."""
        fwi_class = self._scores.get(camera_id)
        if fwi_class == _VERY_LOW:
            return settings.FWI_VERY_LOW_MIN_CONF
        if fwi_class == _LOW:
            return settings.FWI_LOW_MIN_CONF
        return None

    async def refresh(self) -> None:
        """Fetch fresh FWI classes from the risk API. On error, keep the previous cache."""
        if not self.is_configured:
            return
        host = settings.RISK_API_HOST.rstrip("/")  # type: ignore[union-attr]
        url = f"{host}/cameras"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    url,
                    auth=(settings.RISK_API_USERNAME, settings.RISK_API_PASSWORD),  # type: ignore[arg-type]
                )
                response.raise_for_status()
                payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Risk API refresh failed (%s); keeping previous cache (%d entries)", exc, len(self._scores))
            return

        scores: dict[int, str] = {}
        for item in payload:
            camera_id = item.get("id")
            fwi_class = item.get("fwi_class")
            if isinstance(camera_id, int) and isinstance(fwi_class, str):
                scores[camera_id] = fwi_class
        self._scores = scores
        logger.info("Risk API refresh: cached FWI class for %d camera(s)", len(scores))


risk_service = RiskService()
