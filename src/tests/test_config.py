import logging

import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.mark.parametrize(
    "name",
    ["SEQUENCE_RELAXATION_SECONDS", "SEQUENCE_MIN_INTERVAL_SECONDS", "SEQUENCE_CONTINUITY_SECONDS"],
)
def test_settings_reject_non_positive_sequence_windows(name):
    with pytest.raises(ValidationError, match=f"{name} must be > 0"):
        Settings(**{name: 0})


def test_settings_warn_when_continuity_exceeds_relaxation(caplog):
    with caplog.at_level(logging.WARNING, logger="uvicorn.error"):
        Settings(SEQUENCE_CONTINUITY_SECONDS=10, SEQUENCE_RELAXATION_SECONDS=5)
    assert "continuity frames attach past the matchable window" in caplog.text


def test_settings_accept_valid_sequence_windows(caplog):
    with caplog.at_level(logging.WARNING, logger="uvicorn.error"):
        Settings(SEQUENCE_CONTINUITY_SECONDS=120, SEQUENCE_RELAXATION_SECONDS=7200)
    assert "continuity frames" not in caplog.text
