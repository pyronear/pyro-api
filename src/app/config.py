# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import os
import secrets
from typing import Optional

from dotenv import load_dotenv

# load_dotenv(".env_tests" if "pytest" in sys.modules else ".env")
load_dotenv("../.env")

PROJECT_NAME: str = "Pyronear - Alert API"
PROJECT_DESCRIPTION: str = "API for wildfire prevention, detection and monitoring"
API_BASE: str = "api/"
VERSION: str = "0.2.0.dev0"
DEBUG: bool = os.environ.get("DEBUG", "").lower() != "false"
DATABASE_URL: str = os.environ["DATABASE_URL"]
# Fix for SqlAlchemy 1.4+
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL", "")
LOGO_URL: str = "https://pyronear.org/img/logo_letters.png"

ALERT_RELAXATION_SECONDS: int = 30 * 60


SECRET_KEY: str = os.environ.get("SECRET_KEY", secrets.token_urlsafe(32))
if DEBUG:
    # To keep the same Auth at every app loading in debug mode and not having to redo the auth.
    debug_secret_key = "000000000000000000000000000000000000"  # nosec B105
    SECRET_KEY = debug_secret_key

ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
ACCESS_TOKEN_UNLIMITED_MINUTES = 60 * 24 * 365 * 10
JWT_ENCODING_ALGORITHM = "HS256"

SUPERUSER_LOGIN: str = os.environ["SUPERUSER_LOGIN"]
SUPERUSER_PWD: str = os.environ["SUPERUSER_PWD"]

BUCKET_NAME: str = os.environ["BUCKET_NAME"]
BUCKET_MEDIA_FOLDER: Optional[str] = os.getenv("BUCKET_MEDIA_FOLDER")
S3_ACCESS_KEY: str = os.environ["S3_ACCESS_KEY"]
S3_SECRET_KEY: str = os.environ["S3_SECRET_KEY"]
S3_REGION: str = os.environ["S3_REGION"]
S3_ENDPOINT_URL: str = os.environ["S3_ENDPOINT_URL"]
S3_USE_PROXY: bool = os.environ.get("S3_USE_PROXY", "").lower() != "false"
S3_PROXY_URL: str
if S3_USE_PROXY:
    S3_PROXY_URL = os.environ["S3_PROXY_URL"]
else:
    S3_PROXY_URL = ""
DUMMY_BUCKET_FILE = (
    "https://ec.europa.eu/jrc/sites/jrcsh/files/styles/normal-responsive/"
    "public/growing-risk-future-wildfires_adobestock_199370851.jpeg"
)


# Sentry
SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
SENTRY_SERVER_NAME: Optional[str] = os.getenv("SENTRY_SERVER_NAME")

# Telegram
TELEGRAM_TOKEN: Optional[str] = os.getenv("TELEGRAM_TOKEN")
