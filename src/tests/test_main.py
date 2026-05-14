# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import asyncio
from collections.abc import Generator
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI

from app.main import _risk_refresh_loop, _seconds_until_next_utc_hour, lifespan


class _CancelledTask:
    def __init__(self) -> None:
        self.cancel_called = False

    def cancel(self) -> None:
        self.cancel_called = True

    def __await__(self) -> Generator[None, None, None]:
        if not self.cancel_called:
            yield None
        raise asyncio.CancelledError


def test_seconds_until_next_utc_hour_future_today():
    fake_now = datetime(2026, 5, 5, 1, 30, 0, tzinfo=timezone.utc)
    with patch("app.main.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        # datetime.replace + timedelta still need to work — point them at the real type.
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        seconds = _seconds_until_next_utc_hour(4)
    # 04:00 - 01:30 = 2h30m = 9000s
    assert seconds == 2 * 3600 + 30 * 60


def test_seconds_until_next_utc_hour_rolls_to_next_day_when_passed():
    fake_now = datetime(2026, 5, 5, 5, 0, 0, tzinfo=timezone.utc)
    with patch("app.main.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        seconds = _seconds_until_next_utc_hour(4)
    # next 04:00 is tomorrow → 23h
    assert seconds == 23 * 3600


def test_seconds_until_next_utc_hour_clamps_negative_hour():
    fake_now = datetime(2026, 5, 5, 12, 0, 0, tzinfo=timezone.utc)
    with patch("app.main.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        seconds = _seconds_until_next_utc_hour(-5)  # clamped to 0
    # next 00:00 is tomorrow → 12h
    assert seconds == 12 * 3600


def test_seconds_until_next_utc_hour_clamps_overflow_hour():
    fake_now = datetime(2026, 5, 5, 12, 0, 0, tzinfo=timezone.utc)
    with patch("app.main.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        seconds = _seconds_until_next_utc_hour(99)  # clamped to 23
    # next 23:00 today → 11h
    assert seconds == 11 * 3600


def test_seconds_until_next_utc_hour_returns_full_day_when_now_equals_target():
    fake_now = datetime(2026, 5, 5, 4, 0, 0, tzinfo=timezone.utc)
    with patch("app.main.datetime") as mock_dt:
        mock_dt.now.return_value = fake_now
        mock_dt.side_effect = lambda *a, **kw: datetime(*a, **kw)
        seconds = _seconds_until_next_utc_hour(4)
    assert seconds == timedelta(days=1).total_seconds()


@pytest.mark.asyncio
async def test_risk_refresh_loop_calls_refresh_then_cancels_cleanly():
    sleep_mock = AsyncMock(side_effect=[None, asyncio.CancelledError()])
    refresh_mock = AsyncMock()

    with (
        patch("app.main.asyncio.sleep", sleep_mock),
        patch("app.main.risk_service.refresh", new=refresh_mock),
        pytest.raises(asyncio.CancelledError),
    ):
        await _risk_refresh_loop()

    refresh_mock.assert_awaited_once()
    assert sleep_mock.await_count == 2


@pytest.mark.asyncio
async def test_risk_refresh_loop_swallows_refresh_errors_and_continues():
    sleep_mock = AsyncMock(side_effect=[None, None, asyncio.CancelledError()])
    refresh_mock = AsyncMock(side_effect=[RuntimeError("boom"), None])

    with (
        patch("app.main.asyncio.sleep", sleep_mock),
        patch("app.main.risk_service.refresh", new=refresh_mock),
        patch("app.main.logger.exception") as exception_mock,
        pytest.raises(asyncio.CancelledError),
    ):
        await _risk_refresh_loop()

    assert refresh_mock.await_count == 2
    assert sleep_mock.await_count == 3
    exception_mock.assert_called_once_with("Risk refresh loop iteration failed; continuing")


@pytest.mark.asyncio
async def test_lifespan_refreshes_and_cancels_daily_task_when_risk_api_configured():
    fake_service = SimpleNamespace(is_configured=True, refresh=AsyncMock())
    fake_task = _CancelledTask()

    def fake_create_task(coro):
        coro.close()
        return fake_task

    create_task_mock = MagicMock(side_effect=fake_create_task)
    with (
        patch("app.main.risk_service", fake_service),
        patch("app.main.asyncio.create_task", create_task_mock),
    ):
        async with lifespan(FastAPI()):
            fake_service.refresh.assert_awaited_once()
            create_task_mock.assert_called_once()
            assert fake_task.cancel_called is False

    assert fake_task.cancel_called is True


@pytest.mark.asyncio
async def test_lifespan_skips_risk_refresh_when_risk_api_not_configured():
    fake_service = SimpleNamespace(is_configured=False, refresh=AsyncMock())

    with (
        patch("app.main.risk_service", fake_service),
        patch("app.main.asyncio.create_task") as create_task_mock,
    ):
        async with lifespan(FastAPI()):
            fake_service.refresh.assert_not_awaited()
            create_task_mock.assert_not_called()
