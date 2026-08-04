# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.config import settings
from app.services.inference import InferenceService, InferenceUnavailableError


def _fake_httpx_client(*, json_data=None, raise_exc=None, raise_status=None):
    inner = MagicMock()
    if raise_exc is not None:
        inner.post = AsyncMock(side_effect=raise_exc)
    else:
        response = MagicMock()
        response.raise_for_status = MagicMock(side_effect=raise_status)
        response.json = MagicMock(return_value=json_data)
        inner.post = AsyncMock(return_value=response)
    context = MagicMock()
    context.__aenter__ = AsyncMock(return_value=inner)
    context.__aexit__ = AsyncMock(return_value=None)
    return MagicMock(return_value=context), inner


@pytest.fixture
def configured_inference(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "INFERENCE_API_URL", "http://inference.test")
    monkeypatch.setattr(settings, "INFERENCE_API_TOKEN", "secret")


@pytest.mark.asyncio
async def test_triangulate_serializes_datetimes_and_parses_groups(configured_inference):
    factory, inner = _fake_httpx_client(
        json_data={"groups": [{"sequence_ids": [1, 2], "smoke_location": {"lat": 48.3, "lon": 2.7}}]}
    )
    records = [{"id": 1, "started_at": datetime(2026, 1, 1), "last_seen_at": datetime(2026, 1, 1)}]

    with patch("app.services.inference.httpx.AsyncClient", factory):
        groups = await InferenceService().triangulate(records)

    assert groups[0].sequence_ids == (1, 2)
    assert groups[0].smoke_location == pytest.approx((48.3, 2.7))
    args, kwargs = inner.post.await_args
    assert args[0] == "http://inference.test/v1/triangulate"
    assert kwargs["headers"] == {"Authorization": "Bearer secret"}
    assert kwargs["json"]["sequences"][0]["started_at"] == "2026-01-01T00:00:00"


@pytest.mark.asyncio
async def test_timezone_returns_valid_name(configured_inference):
    factory, _ = _fake_httpx_client(json_data={"timezone": "Europe/Paris"})
    with patch("app.services.inference.httpx.AsyncClient", factory):
        assert await InferenceService().timezone(43.3, 5.4) == "Europe/Paris"


@pytest.mark.asyncio
@pytest.mark.parametrize("payload", [{}, {"groups": "bad"}, {"groups": [{"sequence_ids": [], "smoke_location": None}]}])
async def test_triangulate_rejects_malformed_responses(configured_inference, payload):
    factory, _ = _fake_httpx_client(json_data=payload)
    with patch("app.services.inference.httpx.AsyncClient", factory), pytest.raises(InferenceUnavailableError):
        await InferenceService().triangulate([])


@pytest.mark.asyncio
async def test_network_failure_raises_unavailable(configured_inference):
    factory, _ = _fake_httpx_client(raise_exc=httpx.ConnectError("boom"))
    with patch("app.services.inference.httpx.AsyncClient", factory), pytest.raises(InferenceUnavailableError):
        await InferenceService().triangulate([])


@pytest.mark.asyncio
async def test_timeout_raises_unavailable(configured_inference):
    factory, _ = _fake_httpx_client(raise_exc=httpx.ReadTimeout("slow"))
    with patch("app.services.inference.httpx.AsyncClient", factory), pytest.raises(InferenceUnavailableError):
        await InferenceService().triangulate([])


@pytest.mark.asyncio
@pytest.mark.parametrize("status_code", [400, 500])
async def test_http_error_raises_unavailable(configured_inference, status_code):
    request = httpx.Request("POST", "http://inference.test/v1/triangulate")
    response = httpx.Response(status_code, request=request)
    error = httpx.HTTPStatusError("failed", request=request, response=response)
    factory, _ = _fake_httpx_client(raise_status=error)
    with patch("app.services.inference.httpx.AsyncClient", factory), pytest.raises(InferenceUnavailableError):
        await InferenceService().triangulate([])


@pytest.mark.asyncio
async def test_missing_configuration_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "INFERENCE_API_URL", None)
    monkeypatch.setattr(settings, "INFERENCE_API_TOKEN", None)
    with pytest.raises(InferenceUnavailableError):
        await InferenceService().timezone(43.3, 5.4)
