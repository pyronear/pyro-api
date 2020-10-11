import os

PROJECT_NAME: str = 'Pyronear API'
PROJECT_DESCRIPTION: str = 'API for wildfire prevention, detection and monitoring'
API_BASE: str = 'api/'
VERSION: str = "0.1.0a0"
DEBUG: bool = os.environ.get('DEBUG', '') != 'False'
DATABASE_URL: str = os.getenv("DATABASE_URL")
LOGO_URL: str = "https://github.com/pyronear/PyroNear/raw/master/docs/source/_static/img/pyronear-logo-dark.png"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ACCESS_TOKEN_UNLIMITED_MINUTES = 60 * 24 * 365 * 10
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
