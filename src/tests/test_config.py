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


@pytest.mark.parametrize(
    ("issuer", "backchannel_url", "expected_base"),
    [
        (None, None, None),
        ("http://localhost:9310/realms/pyronear/", None, "http://localhost:9310/realms/pyronear"),
        (
            "http://localhost:9310/realms/pyronear",
            "http://keycloak:9310/realms/pyronear",
            "http://keycloak:9310/realms/pyronear",
        ),
    ],
)
def test_settings_keycloak_urls(monkeypatch, issuer, backchannel_url, expected_base):
    for name, value in (("KEYCLOAK_ISSUER", issuer), ("KEYCLOAK_BACKCHANNEL_URL", backchannel_url)):
        if value is None:
            monkeypatch.delenv(name, raising=False)
        else:
            monkeypatch.setenv(name, value)
    settings = Settings()
    if expected_base is None:
        assert settings.keycloak_jwks_url is None
    else:
        assert settings.keycloak_jwks_url == f"{expected_base}/protocol/openid-connect/certs"
    assert issuer == settings.KEYCLOAK_ISSUER


@pytest.mark.parametrize(
    ("name", "expected"),
    [
        ("KEYCLOAK_CLIENT_ID", "pyro-api"),
        ("JWKS_CACHE_SECONDS", 3600),
        ("JWT_LEEWAY_SECONDS", 30),
        ("KEYCLOAK_ISSUER", None),
        ("KEYCLOAK_BACKCHANNEL_URL", None),
    ],
)
def test_settings_blank_keycloak_values_use_defaults(monkeypatch, name, expected):
    monkeypatch.setenv(name, "")
    assert getattr(Settings(), name) == expected
