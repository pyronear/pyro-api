import logging
import secrets

import pytest
from pydantic import ValidationError

from app.core.config import Settings


@pytest.mark.parametrize("secret", [None, ""])
def test_settings_generate_jwt_secret_when_unset_or_empty(monkeypatch, secret):
    if secret is None:
        monkeypatch.delenv("JWT_SECRET", raising=False)
    else:
        monkeypatch.setenv("JWT_SECRET", secret)

    first = Settings().JWT_SECRET
    second = Settings().JWT_SECRET
    assert len(first) >= 32
    assert len(second) >= 32
    assert first != second


def test_settings_preserve_configured_jwt_secret(monkeypatch):
    secret = secrets.token_urlsafe(32)
    monkeypatch.setenv("JWT_SECRET", secret)
    first = Settings().JWT_SECRET
    second = Settings().JWT_SECRET
    assert first == secret
    assert second == secret


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
