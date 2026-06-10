# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.config import settings
from app.core.time import utcnow
from app.services.temporal import TemporalModelService, TemporalUnavailableError


def _fake_httpx_post_client(*, json_data=None, raise_exc=None):
    """Return a factory replacing ``app.services.temporal.httpx.AsyncClient``."""
    inner = MagicMock()
    if raise_exc is not None:
        inner.post = AsyncMock(side_effect=raise_exc)
    else:
        response = MagicMock()
        response.raise_for_status = MagicMock()
        response.json = MagicMock(return_value=json_data)
        inner.post = AsyncMock(return_value=response)

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=inner)
    cm.__aexit__ = AsyncMock(return_value=None)
    return MagicMock(return_value=cm), inner


@pytest.fixture
def configured_temporal(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TEMPORAL_API_URL", "http://temporal.test")


def test_is_available_false_when_not_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "TEMPORAL_API_URL", None)
    assert TemporalModelService().is_available() is False


def test_is_available_true_when_configured(configured_temporal):
    assert TemporalModelService().is_available() is True


@pytest.mark.asyncio
async def test_predict_returns_probability_and_resets_breaker(configured_temporal):
    service = TemporalModelService()
    service._consecutive_failures = 2
    factory, inner = _fake_httpx_post_client(json_data={"is_smoke": True, "probability": 0.73, "model": "m"})
    with patch("app.services.temporal.httpx.AsyncClient", factory):
        prob = await service.predict("bucket-2", ["a.jpg", "b.jpg"])
    assert prob == pytest.approx(0.73)
    assert service._consecutive_failures == 0
    args, kwargs = inner.post.await_args
    assert args[0].endswith("/predict")
    assert kwargs["json"] == {"bucket": "bucket-2", "frames": ["a.jpg", "b.jpg"]}  # no roi key when unset
    assert kwargs["headers"] is None  # no token configured -> no Authorization header


@pytest.mark.asyncio
async def test_predict_sends_roi_when_given(configured_temporal):
    service = TemporalModelService()
    factory, inner = _fake_httpx_post_client(json_data={"probability": 0.5})
    with patch("app.services.temporal.httpx.AsyncClient", factory):
        await service.predict("bucket", ["a.jpg"], roi_xyxyn=[0.1, 0.2, 0.7, 0.8])
    _, kwargs = inner.post.await_args
    assert kwargs["json"] == {"bucket": "bucket", "frames": ["a.jpg"], "roi_xyxyn": [0.1, 0.2, 0.7, 0.8]}


@pytest.mark.asyncio
async def test_predict_sends_bearer_token_when_configured(configured_temporal, monkeypatch):
    monkeypatch.setattr(settings, "TEMPORAL_API_TOKEN", "s3cret")
    service = TemporalModelService()
    factory, inner = _fake_httpx_post_client(json_data={"probability": 0.5})
    with patch("app.services.temporal.httpx.AsyncClient", factory):
        await service.predict("bucket", ["a.jpg"])
    _, kwargs = inner.post.await_args
    assert kwargs["headers"] == {"Authorization": "Bearer s3cret"}


@pytest.mark.asyncio
async def test_predict_returns_none_when_probability_missing(configured_temporal):
    """An uncalibrated/empty probability is a successful call that yields no score."""
    service = TemporalModelService()
    factory, _ = _fake_httpx_post_client(json_data={"is_smoke": False, "probability": None})
    with patch("app.services.temporal.httpx.AsyncClient", factory):
        prob = await service.predict("bucket", ["a.jpg"])
    assert prob is None
    assert service._consecutive_failures == 0  # success, breaker untouched


@pytest.mark.asyncio
async def test_predict_raises_and_records_failure_on_http_error(configured_temporal):
    service = TemporalModelService()
    factory, _ = _fake_httpx_post_client(raise_exc=httpx.ConnectError("boom"))
    with patch("app.services.temporal.httpx.AsyncClient", factory), pytest.raises(TemporalUnavailableError):
        await service.predict("bucket", ["a.jpg"])
    assert service._consecutive_failures == 1


@pytest.mark.asyncio
async def test_breaker_opens_after_three_consecutive_failures(configured_temporal):
    service = TemporalModelService()
    factory, _ = _fake_httpx_post_client(raise_exc=httpx.ConnectError("boom"))
    with patch("app.services.temporal.httpx.AsyncClient", factory):
        for _ in range(TemporalModelService.MAX_CONSECUTIVE_FAILURES):
            with pytest.raises(TemporalUnavailableError):
                await service.predict("bucket", ["a.jpg"])
    assert service.is_available() is False  # breaker is open / paused
    # First trip: base pause (with jitter), not a long blackout.
    pause = service._paused_until - utcnow().timestamp()
    assert pause == pytest.approx(service.BASE_PAUSE_SECONDS, rel=service.JITTER_RATIO + 0.05)


def test_breaker_half_opens_after_pause_elapses(configured_temporal):
    service = TemporalModelService()
    service._consecutive_failures = 3
    service._open_count = 1
    service._paused_until = (utcnow() - timedelta(seconds=1)).timestamp()  # pause already elapsed
    assert service.is_available() is True  # half-open: a probe call is allowed
    assert service._paused_until is None
    assert service._consecutive_failures == 0
    assert service._half_open is True


@pytest.mark.asyncio
async def test_breaker_probe_failure_reopens_immediately_with_backoff(configured_temporal):
    """A failed half-open probe re-opens at the next backoff tier, without 3 more failures."""
    service = TemporalModelService()
    service._open_count = 1
    service._half_open = True  # pause elapsed, probing
    factory, _ = _fake_httpx_post_client(raise_exc=httpx.ConnectError("still down"))
    with patch("app.services.temporal.httpx.AsyncClient", factory), pytest.raises(TemporalUnavailableError):
        await service.predict("bucket", ["a.jpg"])
    assert service.is_available() is False  # re-opened on the single probe failure
    pause = service._paused_until - utcnow().timestamp()
    assert pause == pytest.approx(2 * service.BASE_PAUSE_SECONDS, rel=service.JITTER_RATIO + 0.05)


@pytest.mark.asyncio
async def test_breaker_probe_success_closes(configured_temporal):
    service = TemporalModelService()
    service._open_count = 3
    service._half_open = True
    factory, _ = _fake_httpx_post_client(json_data={"probability": 0.5})
    with patch("app.services.temporal.httpx.AsyncClient", factory):
        assert await service.predict("bucket", ["a.jpg"]) == pytest.approx(0.5)
    assert service._half_open is False
    assert service._open_count == 0  # fully closed: a future outage backs off from the base again
    assert service.is_available() is True


def test_breaker_backoff_is_capped(configured_temporal):
    service = TemporalModelService()
    service._open_count = 20  # far past the cap
    service._open()
    pause = service._paused_until - utcnow().timestamp()
    assert pause <= service.MAX_PAUSE_SECONDS * (1 + service.JITTER_RATIO) + 1


@pytest.mark.asyncio
async def test_4xx_fails_the_call_but_does_not_trip_the_breaker(configured_temporal):
    """A 4xx signals a config/input problem, not an outage: fail open without pausing."""
    service = TemporalModelService()
    request = httpx.Request("POST", "http://temporal.test/predict")
    response = httpx.Response(401, request=request)
    factory, _ = _fake_httpx_post_client(raise_exc=httpx.HTTPStatusError("auth", request=request, response=response))
    with patch("app.services.temporal.httpx.AsyncClient", factory):
        for _ in range(TemporalModelService.MAX_CONSECUTIVE_FAILURES + 2):
            with pytest.raises(TemporalUnavailableError):
                await service.predict("bucket", ["a.jpg"])
    assert service._consecutive_failures == 0  # not counted as outage
    assert service.is_available() is True  # breaker never opened


@pytest.mark.asyncio
async def test_5xx_counts_toward_the_breaker(configured_temporal):
    service = TemporalModelService()
    request = httpx.Request("POST", "http://temporal.test/predict")
    response = httpx.Response(503, request=request)
    factory, _ = _fake_httpx_post_client(raise_exc=httpx.HTTPStatusError("down", request=request, response=response))
    with patch("app.services.temporal.httpx.AsyncClient", factory):
        for _ in range(TemporalModelService.MAX_CONSECUTIVE_FAILURES):
            with pytest.raises(TemporalUnavailableError):
                await service.predict("bucket", ["a.jpg"])
    assert service.is_available() is False  # outage: breaker opened
