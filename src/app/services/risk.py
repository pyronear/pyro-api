# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import logging
from datetime import date
from typing import Union

import httpx

from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

__all__ = ["min_confidence_for_class", "risk_service"]


def min_confidence_for_class(fwi_class: Union[str, None]) -> Union[float, None]:
    """Return the min confidence required for this FWI class, or None if no filter applies."""
    if not fwi_class:
        return None
    table = {"very_low": settings.FWI_VERY_LOW_MIN_CONF, "low": settings.FWI_LOW_MIN_CONF}
    return table.get(fwi_class.strip().lower().replace(" ", "_"))


def _parse_scores_payload(payload: object) -> dict[int, str]:
    """Pull ``{camera_id: fwi_class}`` from a list of risk-api items. Skip malformed rows."""
    if not isinstance(payload, list):
        return {}
    scores: dict[int, str] = {}
    for item in payload:
        if not isinstance(item, dict):
            continue
        cid = item.get("id") or item.get("camera_id")
        fwi = item.get("fwi_class")
        if isinstance(cid, int) and isinstance(fwi, str):
            scores[cid] = fwi
    return scores


class RiskService:
    """In-memory cache of the daily FWI class per camera.

    Refreshed once at startup and once a day from the pyro-risk-api service.
    Fail-open: if the API is unreachable or a camera is unknown, no filter is applied.
    """

    def __init__(self) -> None:
        self._scores: dict[int, str] = {}

    @property
    def is_configured(self) -> bool:
        return bool(settings.RISK_API_URL and settings.RISK_API_LOGIN and settings.RISK_API_PWD)

    def class_for_camera(self, camera_id: int) -> Union[str, None]:
        """Return today's cached FWI class for a camera, or None if unknown."""
        return self._scores.get(camera_id)

    def min_confidence(self, camera_id: int) -> Union[float, None]:
        """Return the min confidence required for this camera (today), or None if no filter."""
        return min_confidence_for_class(self._scores.get(camera_id))

    async def _fetch(self, path: str, params: Union[dict, None] = None) -> object:
        if not self.is_configured:
            return None
        host = settings.RISK_API_URL.rstrip("/")  # type: ignore[union-attr]
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    f"{host}/{path.lstrip('/')}",
                    params=params,
                    auth=(settings.RISK_API_LOGIN, settings.RISK_API_PWD),  # type: ignore[arg-type]
                )
                response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Risk API call %s failed (%s)", path, exc)
            return None

    async def refresh(self) -> None:
        """Fetch fresh FWI classes from the risk API. On network/HTTP failure, keep the previous cache."""
        payload = await self._fetch("cameras")
        if payload is None:
            logger.warning("Risk API refresh failed; keeping previous cache (%d entries)", len(self._scores))
            return
        self._scores = _parse_scores_payload(payload)
        logger.info("Risk API refresh: cached FWI class for %d camera(s)", len(self._scores))

    async def get_scores_for_date(self, target_date: date, organization_id: Union[int, None] = None) -> dict[int, str]:
        """Fetch persisted FWI classes for a specific date, optionally scoped to an organization.

        Returns {} on error or when not configured.
        """
        params = {"organization_id": organization_id} if organization_id is not None else None
        return _parse_scores_payload(await self._fetch(f"scores/{target_date.isoformat()}", params=params))


risk_service = RiskService()
