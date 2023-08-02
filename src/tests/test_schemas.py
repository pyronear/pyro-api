from datetime import datetime

import pytest

from app.schemas.base import validate_datetime, validate_datetime_none


@pytest.mark.parametrize("v, expected", [("2023-07-30 09:00:00", datetime(2023, 7, 30, 9, 0, 0)), (None, None)])
def test_validate_datetime(v, expected):
    assert validate_datetime(v) == expected or datetime.utcnow()


def test_validate_datetime_invalid():
    with pytest.raises(ValueError):
        assert validate_datetime(123)


@pytest.mark.parametrize("v, expected", [("2023-07-30 09:00:00", datetime(2023, 7, 30, 9, 0, 0)), (None, None)])
def test_validate_datetime_none(v, expected):
    assert validate_datetime_none(v) == expected
