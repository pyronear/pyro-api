# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import pytest

from app.core.config import settings
from app.services.risk import RiskService, min_confidence_for_class


def test_min_confidence_for_class():
    assert min_confidence_for_class("very_low") == settings.FWI_VERY_LOW_MIN_CONF
    assert min_confidence_for_class("low") == settings.FWI_LOW_MIN_CONF
    assert min_confidence_for_class("moderate") is None
    assert min_confidence_for_class("high") is None
    assert min_confidence_for_class("very_high") is None
    assert min_confidence_for_class("extreme") is None
    assert min_confidence_for_class(None) is None
    assert min_confidence_for_class("unexpected") is None


def test_risk_service_min_confidence_uses_cached_class():
    service = RiskService()
    service._scores = {1: "very_low", 2: "low", 3: "moderate"}
    assert service.min_confidence(1) == settings.FWI_VERY_LOW_MIN_CONF
    assert service.min_confidence(2) == settings.FWI_LOW_MIN_CONF
    assert service.min_confidence(3) is None
    assert service.min_confidence(99) is None


@pytest.mark.asyncio
async def test_refresh_no_op_when_not_configured(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(settings, "RISK_API_HOST", None)
    service = RiskService()
    service._scores = {1: "low"}
    await service.refresh()
    assert service._scores == {1: "low"}
