# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import logging
from datetime import timedelta
from typing import List, Union

import httpx

from app.core.config import settings
from app.core.time import utcnow

logger = logging.getLogger("uvicorn.error")

__all__ = ["temporal_service"]


class TemporalModelService:
    """Client for the temporal smoke classifier API with an in-memory circuit breaker.

    The model needs an ordered window of frame keys. We only query a sequence once it
    holds between ``MIN_FRAMES`` and ``MAX_FRAMES`` distinct frames, sending the last
    ``WINDOW`` frames. After ``MAX_CONSECUTIVE_FAILURES`` failed calls in a row, calls
    are paused for ``PAUSE_SECONDS`` (the breaker), during which the caller fails open.

    State is per-process, like the risk cache.
    """

    MIN_FRAMES: int = 4
    MAX_FRAMES: int = 10
    WINDOW: int = 6
    MAX_CONSECUTIVE_FAILURES: int = 3
    PAUSE_SECONDS: int = 4 * 3600
    TIMEOUT_SECONDS: float = 10.0

    def __init__(self) -> None:
        self._consecutive_failures: int = 0
        self._paused_until: Union[float, None] = None

    @property
    def is_configured(self) -> bool:
        return bool(settings.TEMPORAL_API_URL)

    def is_available(self) -> bool:
        """True when configured and not currently paused by the breaker."""
        if not self.is_configured:
            return False
        if self._paused_until is not None:
            if utcnow().timestamp() < self._paused_until:
                return False
            # Pause elapsed: half-open, reset and allow a retry.
            self._paused_until = None
            self._consecutive_failures = 0
        return True

    def _record_success(self) -> None:
        self._consecutive_failures = 0
        self._paused_until = None

    def _record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            self._paused_until = (utcnow() + timedelta(seconds=self.PAUSE_SECONDS)).timestamp()
            logger.warning("Temporal API breaker opened for %ds after repeated failures", self.PAUSE_SECONDS)

    async def predict(self, bucket: str, frames: List[str]) -> Union[float, None]:
        """Return the smoke probability for the given frames, or None on failure.

        Records success/failure for the circuit breaker. A successful call that carries
        no calibrated probability also returns None.
        """
        host = (settings.TEMPORAL_API_URL or "").rstrip("/")
        try:
            async with httpx.AsyncClient(timeout=self.TIMEOUT_SECONDS) as client:
                response = await client.post(f"{host}/predict", json={"bucket": bucket, "frames": frames})
                response.raise_for_status()
                data = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Temporal API call failed (%s)", exc)
            self._record_failure()
            return None
        self._record_success()
        probability = data.get("probability") if isinstance(data, dict) else None
        return float(probability) if isinstance(probability, (int, float)) else None


temporal_service = TemporalModelService()
