from datetime import datetime, timezone

from app.core.time import utcnow


def test_utcnow_returns_naive_datetime():
    result = utcnow()
    assert isinstance(result, datetime)
    assert result.tzinfo is None


def test_utcnow_matches_wall_clock():
    before = datetime.now(timezone.utc).replace(tzinfo=None)
    result = utcnow()
    after = datetime.now(timezone.utc).replace(tzinfo=None)
    assert before <= result <= after


def test_utcnow_is_monotonic_across_quick_calls():
    first = utcnow()
    second = utcnow()
    assert first <= second
