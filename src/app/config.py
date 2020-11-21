import os
import secrets


PROJECT_NAME: str = 'Pyronear API'
PROJECT_DESCRIPTION: str = 'API for wildfire prevention, detection and monitoring'
API_BASE: str = 'api/'
VERSION: str = "0.1.0a0"
DEBUG: bool = os.environ.get('DEBUG', '') != 'False'
DATABASE_URL: str = os.getenv("DATABASE_URL")
LOGO_URL: str = "https://github.com/pyronear/PyroNear/raw/master/docs/source/_static/img/pyronear-logo-dark.png"


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

BUCKET_NAME: str = "mypyroneartest"
