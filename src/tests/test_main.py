# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.main import _seconds_until_next_utc_hour


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
