# Copyright (C) 2024, Pyronear.

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
    SUPPORT_EMAIL: Union[str, None] = os.environ.get("SUPPORT_EMAIL")
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

    # Storage
    S3_BUCKET_NAME: str = os.environ["S3_BUCKET_NAME"]
    S3_ACCESS_KEY: str = os.environ["S3_ACCESS_KEY"]
    S3_SECRET_KEY: str = os.environ["S3_SECRET_KEY"]
    S3_REGION: str = os.environ["S3_REGION"]
    S3_ENDPOINT_URL: str = os.environ["S3_ENDPOINT_URL"]
    S3_PROXY_URL: str = os.environ.get("S3_PROXY_URL", "")
    S3_URL_EXPIRATION: int = int(os.environ.get("S3_URL_EXPIRATION") or 24 * 3600)

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
