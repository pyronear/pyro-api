# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import logging
import random
from datetime import timedelta
from typing import List, NamedTuple, Union

import httpx

from app.core.config import settings
from app.core.time import utcnow

logger = logging.getLogger("uvicorn.error")

__all__ = ["TemporalPrediction", "TemporalUnavailableError", "temporal_service"]


class TemporalUnavailableError(Exception):
    """Raised when a temporal API call fails (network/HTTP). Distinct from a scoreless response."""


class TemporalPrediction(NamedTuple):
    """A /predict result: the score plus the model/code versions that produced it.

    ``probability`` is None for a successful but scoreless (uncalibrated) response. The
    versions are persisted next to the score so every stored score stays attributable to
    the exact model release and serving-code image after redeploys (offline evaluation
    against the ``is_wildfire`` ground truth, per-version threshold tuning).
    """

    probability: Union[float, None]
    model_version: Union[str, None] = None
    api_version: Union[str, None] = None


class TemporalModelService:
    """Client for the temporal smoke classifier API with an in-memory circuit breaker.

    The model needs an ordered list of frame keys; the validation worker queries a sequence
    once it holds at least ``MIN_FRAMES`` distinct frames (window rules live in the worker).

    Concurrency: the temporal API itself serializes inference server-side (single process,
    lock around the model), so this client enforces no limit. Each pyro-api process runs one
    validation worker, so with N uvicorn workers at most N calls are in flight — safe as
    long as ``N * model_latency < TEMPORAL_API_TIMEOUT``.

    Breaker: after ``MAX_CONSECUTIVE_FAILURES`` outage-like failures (network errors, 5xx)
    in a row, calls are paused with exponential backoff — ``BASE_PAUSE_SECONDS`` doubled on
    each re-trip up to ``MAX_PAUSE_SECONDS``, with jitter. Once the pause elapses the breaker
    is half-open: the next call is a probe; success closes the breaker, failure re-opens it
    immediately at the next backoff tier (no need for 3 more failures). 4xx responses fail
    the call (callers fail open) but CLOSE the breaker: the API answered, so it's reachable —
    a config/input problem, not an outage. State is per-process, like the risk cache: with N
    uvicorn workers each process keeps its own breaker.
    """

    MIN_FRAMES: int = 4
    MAX_FRAMES: int = 10
    MAX_CONSECUTIVE_FAILURES: int = 3
    BASE_PAUSE_SECONDS: float = 60.0
    MAX_PAUSE_SECONDS: float = 3600.0
    JITTER_RATIO: float = 0.2

    def __init__(self) -> None:
        self._consecutive_failures: int = 0
        self._open_count: int = 0
        self._paused_until: Union[float, None] = None
        self._half_open: bool = False

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
            # Pause elapsed: half-open — allow a probe call, but remember we were open so a
            # probe failure re-opens immediately at the next backoff tier.
            self._paused_until = None
            self._consecutive_failures = 0
            self._half_open = True
        return True

    def _record_success(self) -> None:
        self._consecutive_failures = 0
        self._open_count = 0
        self._paused_until = None
        self._half_open = False

    def _open(self) -> None:
        self._open_count += 1
        pause = min(self.BASE_PAUSE_SECONDS * 2 ** (self._open_count - 1), self.MAX_PAUSE_SECONDS)
        pause *= 1 + random.uniform(-self.JITTER_RATIO, self.JITTER_RATIO)  # noqa: S311 - jitter, not crypto
        self._paused_until = (utcnow() + timedelta(seconds=pause)).timestamp()
        self._half_open = False
        logger.warning("Temporal API breaker opened for %.0fs (trip #%d)", pause, self._open_count)

    def _record_failure(self) -> None:
        self._consecutive_failures += 1
        if self._half_open or self._consecutive_failures >= self.MAX_CONSECUTIVE_FAILURES:
            self._open()

    async def predict(
        self, bucket: str, frames: List[str], roi_xyxyn: Union[List[float], None] = None
    ) -> TemporalPrediction:
        """Return the smoke probability for the given frames, with version provenance.

        ``roi_xyxyn`` (normalized [x_min, y_min, x_max, y_max] corners) scopes the verdict
        to the sequence's region so unrelated activity in the frame can't pollute it.

        Records success/failure for the circuit breaker (4xx fails the call but closes the
        breaker — the API answered). The returned probability is ``None`` for a successful
        call that carries no calibrated probability. Raises
        :class:`TemporalUnavailableError` when the call itself fails, so callers can fail
        open.

        Sends ``Authorization: Bearer`` when ``TEMPORAL_API_TOKEN`` is set (the temporal API
        guards /predict with a shared token); unset matches a server with auth disabled.
        """
        host = (settings.TEMPORAL_API_URL or "").rstrip("/")
        headers = {"Authorization": f"Bearer {settings.TEMPORAL_API_TOKEN}"} if settings.TEMPORAL_API_TOKEN else None
        payload: dict = {"bucket": bucket, "frames": frames}
        if roi_xyxyn is not None:
            payload["roi_xyxyn"] = roi_xyxyn
        try:
            async with httpx.AsyncClient(timeout=settings.TEMPORAL_API_TIMEOUT) as client:
                response = await client.post(f"{host}/predict", json=payload, headers=headers)
                response.raise_for_status()
                data = response.json()
        except httpx.HTTPStatusError as exc:
            logger.warning("Temporal API call failed: %r", exc)
            if exc.response.status_code < 500:
                # Config/input problem (auth, bad payload), not an outage: the API answered,
                # so it's reachable — close the breaker, but fail the call so the caller
                # fails open.
                self._record_success()
            else:
                self._record_failure()
            raise TemporalUnavailableError(str(exc)) from exc
        except (httpx.HTTPError, ValueError) as exc:
            logger.warning("Temporal API call failed: %r", exc)
            self._record_failure()
            raise TemporalUnavailableError(str(exc)) from exc
        self._record_success()
        probability = data.get("probability") if isinstance(data, dict) else None
        # The response's "version" block ({"api": ..., "model": ...}) carries the serving
        # image tag and the packaged model release; absent on older servers, values null on
        # non-release builds.
        version = data.get("version") if isinstance(data, dict) else None
        version = version if isinstance(version, dict) else {}
        return TemporalPrediction(
            probability=float(probability) if isinstance(probability, (int, float)) else None,
            model_version=str(version["model"]) if version.get("model") is not None else None,
            api_version=str(version["api"]) if version.get("api") is not None else None,
        )


temporal_service = TemporalModelService()
