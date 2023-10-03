from contextlib import nullcontext
from datetime import datetime

import pytest

from app.schemas.alerts import validate_localization
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


@pytest.mark.parametrize(
    "value, error",
    [
        (None, nullcontext()),
        ("[]", nullcontext()),
        ("[[0, 0, 1, 1, 1]]", nullcontext()),
        ([], pytest.raises(ValueError)),
        ("something else", pytest.raises(ValueError)),
        ("[[0, 0, 1, 1]]", pytest.raises(ValueError)),
    ],
)
def test_validate_localization(value, error):
    with error:
        validate_localization(value)
