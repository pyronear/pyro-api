import os
import secrets


PROJECT_NAME: str = "Pyronear API"
PROJECT_DESCRIPTION: str = "API for wildfire prevention, detection and monitoring"
API_BASE: str = "api/"
VERSION: str = "0.1.0a0"
DEBUG: bool = os.environ.get("DEBUG", "") != "False"
DATABASE_URL: str = os.getenv("DATABASE_URL")
LOGO_URL: str = "https://github.com/pyronear/PyroNear/raw/master/docs/source/_static/img/pyronear-logo-dark.png"

SECRET_KEY: str = secrets.token_urlsafe(32)
ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
