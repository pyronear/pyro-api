# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.config import settings
from app.services.risk import FWI_MIN_CONF, RiskService, min_confidence_for_class


def _fake_httpx_client(*, json_data=None, raise_exc=None, side_effect_per_call=None):
    """Return a context manager replacing ``app.services.risk.httpx.AsyncClient``.

    Either pass ``json_data`` (single response), ``raise_exc`` (raised on get()), or
    ``side_effect_per_call`` (list of (json_or_exc) values returned in order).
    """
    response = MagicMock()
    response.raise_for_status = MagicMock()
    response.json = MagicMock(return_value=json_data)

    inner = MagicMock()
    if raise_exc is not None:
        inner.get = AsyncMock(side_effect=raise_exc)
    elif side_effect_per_call is not None:
        responses = []
        for item in side_effect_per_call:
            if isinstance(item, Exception):
                responses.append(item)
            else:
                r = MagicMock()
                r.raise_for_status = MagicMock()
                r.json = MagicMock(return_value=item)
                responses.append(r)
        inner.get = AsyncMock(side_effect=responses)
    else:
        inner.get = AsyncMock(return_value=response)

    cm = MagicMock()
    cm.__aenter__ = AsyncMock(return_value=inner)
    cm.__aexit__ = AsyncMock(return_value=None)

    factory = MagicMock(return_value=cm)
    return factory, inner


@pytest.fixture
def configured_risk(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "RISK_API_URL", "http://risk.test")
    monkeypatch.setattr(settings, "RISK_API_LOGIN", "u")
    monkeypatch.setattr(settings, "RISK_API_PWD", "p")


def test_min_confidence_for_class():
    assert min_confidence_for_class("very_low") == FWI_MIN_CONF["very_low"]
    assert min_confidence_for_class("low") == FWI_MIN_CONF["low"]
    assert min_confidence_for_class("moderate") is None
    assert min_confidence_for_class("high") is None
    assert min_confidence_for_class("very_high") is None
    assert min_confidence_for_class("extreme") is None
    assert min_confidence_for_class(None) is None
    assert min_confidence_for_class("unexpected") is None


def test_min_confidence_for_class_normalizes_casing():
    assert min_confidence_for_class("Very Low") == FWI_MIN_CONF["very_low"]
    assert min_confidence_for_class("LOW") == FWI_MIN_CONF["low"]
    assert min_confidence_for_class("  very_low  ") == FWI_MIN_CONF["very_low"]


def test_risk_service_min_confidence_uses_cached_class():
    service = RiskService()
    service._scores = {1: "very_low", 2: "low", 3: "moderate"}
    assert service.min_confidence(1) == FWI_MIN_CONF["very_low"]
    assert service.min_confidence(2) == FWI_MIN_CONF["low"]
    assert service.min_confidence(3) is None
    assert service.min_confidence(99) is None


@pytest.mark.asyncio
async def test_refresh_no_op_when_not_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "RISK_API_URL", None)
    service = RiskService()
    service._scores = {1: "low"}
    await service.refresh()
    assert service._scores == {1: "low"}


@pytest.mark.asyncio
async def test_refresh_replaces_cache_on_success(configured_risk):
    service = RiskService()
    service._scores = {99: "very_low"}  # stale entry that should disappear
    factory, inner = _fake_httpx_client(
        json_data=[
            {"id": 1, "fwi_class": "very_low"},
            {"id": 2, "fwi_class": "moderate"},
        ]
    )
    with patch("app.services.risk.httpx.AsyncClient", factory):
        await service.refresh()
    assert service._scores == {1: "very_low", 2: "moderate"}
    inner.get.assert_awaited_once()
    args, kwargs = inner.get.await_args
    assert args[0].endswith("/cameras")
    assert kwargs["auth"] == ("u", "p")


@pytest.mark.asyncio
async def test_refresh_keeps_cache_on_http_error(configured_risk):
    service = RiskService()
    service._scores = {1: "low"}
    factory, _ = _fake_httpx_client(raise_exc=httpx.ConnectError("boom"))
    with patch("app.services.risk.httpx.AsyncClient", factory):
        await service.refresh()
    assert service._scores == {1: "low"}


@pytest.mark.asyncio
async def test_refresh_replaces_with_empty_when_payload_is_empty_list(configured_risk):
    """Empty list from upstream wipes the cache; only a network/HTTP failure preserves it."""
    service = RiskService()
    service._scores = {1: "low"}
    factory, _ = _fake_httpx_client(json_data=[])
    with patch("app.services.risk.httpx.AsyncClient", factory):
        await service.refresh()
    assert service._scores == {}


@pytest.mark.asyncio
async def test_refresh_skips_malformed_rows(configured_risk):
    service = RiskService()
    factory, _ = _fake_httpx_client(
        json_data=[
            {"id": 1, "fwi_class": "low"},
            "not-a-dict",
            {"id": "bad", "fwi_class": "low"},
            {"id": 2},
            {"camera_id": 3, "fwi_class": "very_low"},
        ]
    )
    with patch("app.services.risk.httpx.AsyncClient", factory):
        await service.refresh()
    assert service._scores == {1: "low", 3: "very_low"}


@pytest.mark.asyncio
async def test_get_scores_for_date_passes_organization_param(configured_risk):
    service = RiskService()
    factory, inner = _fake_httpx_client(json_data=[{"camera_id": 7, "fwi_class": "high"}])
    with patch("app.services.risk.httpx.AsyncClient", factory):
        scores = await service.get_scores_for_date(date(2026, 5, 5), organization_id=42)
    assert scores == {7: "high"}
    args, kwargs = inner.get.await_args
    assert args[0].endswith("/scores/2026-05-05")
    assert kwargs["params"] == {"organization_id": 42}


@pytest.mark.asyncio
async def test_get_scores_for_date_returns_empty_on_failure(configured_risk):
    service = RiskService()
    factory, _ = _fake_httpx_client(raise_exc=httpx.ReadTimeout("slow"))
    with patch("app.services.risk.httpx.AsyncClient", factory):
        scores = await service.get_scores_for_date(date(2026, 5, 5))
    assert scores == {}


@pytest.mark.asyncio
async def test_get_scores_for_date_no_org_param_when_none(configured_risk):
    service = RiskService()
    factory, inner = _fake_httpx_client(json_data=[])
    with patch("app.services.risk.httpx.AsyncClient", factory):
        await service.get_scores_for_date(date(2026, 5, 5))
    _, kwargs = inner.get.await_args
    assert kwargs["params"] is None
