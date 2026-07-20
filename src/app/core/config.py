# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import os
import secrets
import socket
from typing import Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

__all__ = ["settings"]


class Settings(BaseSettings):
    # State
    PROJECT_NAME: str = "Pyronear - Wildfire Alert API"
    PROJECT_DESCRIPTION: str = "API for wildfire prevention, detection and monitoring"
    VERSION: str = "0.2.0.dev0"
    API_V1_STR: str = "/api/v1"
    CORS_ORIGIN: str = "*"
    SUPPORT_EMAIL: str = os.environ.get("SUPPORT_EMAIL", "support@pyronear.org")
    # Authentication
    SUPERADMIN_LOGIN: str = os.environ["SUPERADMIN_LOGIN"]
    SUPERADMIN_PWD: str = os.environ["SUPERADMIN_PWD"]
    SUPERADMIN_ORG: str = os.environ["SUPERADMIN_ORG"]
    # DB
    POSTGRES_URL: str = os.environ["POSTGRES_URL"]

    @field_validator("POSTGRES_URL")
    @classmethod
    def sqlachmey_uri(cls, v: str) -> str:
        # Fix for SqlAlchemy 1.4+
        if v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        return v

    # Security
    JWT_SECRET: str = os.environ.get("JWT_SECRET") or secrets.token_urlsafe(32)
    JWT_EXPIRE_MINUTES: int = 60
    JWT_UNLIMITED: int = 60 * 24 * 365
    JWT_ALGORITHM: str = "HS256"

    # DB conversion
    MAX_BOXES_PER_DETECTION: int = 5
    DECIMALS_PER_COORD: int = 3
    MAX_BBOX_STR_LENGTH: int = (
        2 + MAX_BOXES_PER_DETECTION * (2 + 5 * (2 + DECIMALS_PER_COORD) + 4 * 2) + (MAX_BOXES_PER_DETECTION - 1) * 2
    )
    # Single bbox (for Detection.bbox field): max 1 box
    MAX_BBOX_STR_LENGTH_SINGLE: int = 2 + 1 * (2 + 5 * (2 + DECIMALS_PER_COORD) + 4 * 2) + (1 - 1) * 2
    # Other bboxes (for Detection.others_bboxes): max MAX_BOXES_PER_DETECTION boxes minus 1
    MAX_BBOX_STR_LENGTH_OTHERS: int = (
        2
        + (MAX_BOXES_PER_DETECTION - 1) * (2 + 5 * (2 + DECIMALS_PER_COORD) + 4 * 2)
        + ((MAX_BOXES_PER_DETECTION - 1) - 1) * 2
    )

    # Storage
    S3_ACCESS_KEY: str = os.environ["S3_ACCESS_KEY"]
    S3_SECRET_KEY: str = os.environ["S3_SECRET_KEY"]
    S3_REGION: str = os.environ["S3_REGION"]
    S3_ENDPOINT_URL: str = os.environ["S3_ENDPOINT_URL"]
    S3_PROXY_URL: str = os.environ.get("S3_PROXY_URL", "")
    S3_URL_EXPIRATION: int = int(os.environ.get("S3_URL_EXPIRATION") or 24 * 3600)

    # Sequence handling
    SEQUENCE_RELAXATION_SECONDS: int = int(os.environ.get("SEQUENCE_RELAXATION_SECONDS") or 120 * 60)
    SEQUENCE_MIN_INTERVAL_DETS: int = int(os.environ.get("SEQUENCE_MIN_INTERVAL_DETS") or 3)
    SEQUENCE_MIN_INTERVAL_SECONDS: int = int(os.environ.get("SEQUENCE_MIN_INTERVAL_SECONDS") or 5 * 60)
    # Max gap (relative image coords) between two bboxes still considered the same smoke plume.
    SEQUENCE_BBOX_TOLERANCE: float = float(os.environ.get("SEQUENCE_BBOX_TOLERANCE") or 0.05)
    TRIANGULATION_RELAXATION_SECONDS: int = int(os.environ.get("TRIANGULATION_RELAXATION_SECONDS") or 30 * 60)
    # Cameras closer than this share an apex: their cone intersection cannot localize smoke.
    TRIANGULATION_MIN_APEX_DISTANCE_KM: float = float(os.environ.get("TRIANGULATION_MIN_APEX_DISTANCE_KM") or 0.1)
    ALERT_MERGE_MAX_DISTANCE_KM: float = float(os.environ.get("ALERT_MERGE_MAX_DISTANCE_KM") or 2.0)

    # Notifications
    TELEGRAM_TOKEN: Union[str, None] = os.environ.get("TELEGRAM_TOKEN")
    PLATFORM_URL: str = os.environ.get("PLATFORM_URL", "")

    # Temporal model API (validates sequences from their frames)
    TEMPORAL_API_URL: Union[str, None] = os.environ.get("TEMPORAL_API_URL")
    # Shared bearer token for /predict; empty = server has auth disabled, send no header.
    TEMPORAL_API_TOKEN: Union[str, None] = os.environ.get("TEMPORAL_API_TOKEN") or None
    TEMPORAL_MODEL_THRESHOLD: float = float(os.environ.get("TEMPORAL_MODEL_THRESHOLD") or 0.45)
    # Generous timeout: the temporal API serializes inference server-side, so with N uvicorn
    # workers a call can wait behind N-1 others; keep N * model latency under this value.
    TEMPORAL_API_TIMEOUT: float = float(os.environ.get("TEMPORAL_API_TIMEOUT") or 30.0)
    # Validation worker (one loop per uvicorn process, coordinated through the DB):
    # idle poll interval for due sequences,
    TEMPORAL_VALIDATION_POLL_SECONDS: float = float(os.environ.get("TEMPORAL_VALIDATION_POLL_SECONDS") or 2.0)
    # max time a sequence may wait in the queue before failing open on the risk gate alone
    # (bounds validation latency under a backlog; traced as validation_status=fail_open_stale),
    TEMPORAL_VALIDATION_MAX_AGE: float = float(os.environ.get("TEMPORAL_VALIDATION_MAX_AGE") or 300.0)
    # and how long a claimed job is leased before a sibling worker may retry it (must exceed
    # TEMPORAL_API_TIMEOUT plus the DB phases).
    TEMPORAL_VALIDATION_LEASE_SECONDS: float = float(os.environ.get("TEMPORAL_VALIDATION_LEASE_SECONDS") or 120.0)

    # Risk API (daily fire-weather index per camera)
    RISK_API_URL: Union[str, None] = os.environ.get("RISK_API_URL")
    RISK_API_LOGIN: Union[str, None] = os.environ.get("RISK_API_LOGIN")
    RISK_API_PWD: Union[str, None] = os.environ.get("RISK_API_PWD")
    RISK_REFRESH_HOUR_UTC: int = int(os.environ.get("RISK_REFRESH_HOUR_UTC") or 4)

    # Error monitoring
    SENTRY_DSN: Union[str, None] = os.environ.get("SENTRY_DSN")
    SERVER_NAME: str = os.environ.get("SERVER_NAME", socket.gethostname())

    @field_validator("SENTRY_DSN")
    @classmethod
    def sentry_dsn_can_be_blank(cls, v: str) -> Union[str, None]:
        if not isinstance(v, str) or len(v) == 0:
            return None
        return v

    # Product analytics
    POSTHOG_HOST: str = os.getenv("POSTHOG_HOST", "https://eu.posthog.com")
    POSTHOG_KEY: Union[str, None] = os.environ.get("POSTHOG_KEY")

    @field_validator("POSTHOG_KEY")
    @classmethod
    def posthog_key_can_be_blank(cls, v: str) -> Union[str, None]:
        if not isinstance(v, str) or len(v) == 0:
            return None
        return v

    DEBUG: bool = os.environ.get("DEBUG", "").lower() != "false"
    LOGO_URL: str = ""
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "").lower() == "true"

    model_config = SettingsConfigDict(case_sensitive=True)


settings = Settings()
