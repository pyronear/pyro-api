import os
import secrets
from typing import Optional


PROJECT_NAME: str = 'Pyronear API'
PROJECT_DESCRIPTION: str = 'API for wildfire prevention, detection and monitoring'
API_BASE: str = 'api/'
VERSION: str = "0.1.2a0"
DEBUG: bool = os.environ.get('DEBUG', '') != 'False'
DATABASE_URL: str = os.getenv("DATABASE_URL")
TEST_DATABASE_URL: str = os.getenv("TEST_DATABASE_URL")
LOGO_URL: str = "https://pyronear.org/img/logo_letters.png"


SECRET_KEY: str = secrets.token_urlsafe(32)
if DEBUG:
    # To keep the same Auth at every app loading in debug mode and not having to redo the auth.
    debug_secret_key = "000000000000000000000000000000000000"
    SECRET_KEY = debug_secret_key

ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
ACCESS_TOKEN_UNLIMITED_MINUTES = 60 * 24 * 365 * 10
JWT_ENCODING_ALGORITHM = "HS256"

SUPERUSER_LOGIN: str = os.getenv("SUPERUSER_LOGIN")
SUPERUSER_PWD: str = os.getenv("SUPERUSER_PWD")

if SUPERUSER_LOGIN is None or SUPERUSER_PWD is None:
    raise ValueError(
        "Missing Credentials. Please set 'SUPERUSER_LOGIN' and 'SUPERUSER_PWD' in your environment variables")

QARNOT_TOKEN: str = os.getenv("QARNOT_TOKEN")
BUCKET_NAME: str = os.getenv("BUCKET_NAME")
BUCKET_MEDIA_FOLDER: Optional[str] = os.getenv("BUCKET_MEDIA_FOLDER")
DUMMY_BUCKET_FILE = "https://ec.europa.eu/jrc/sites/jrcsh/files/styles/normal-responsive/" \
                    + "public/growing-risk-future-wildfires_adobestock_199370851.jpeg"


# Sentry
SENTRY_DSN: Optional[str] = os.getenv("SENTRY_DSN")
SERVER_NAME: Optional[str] = os.getenv("SERVER_NAME")
