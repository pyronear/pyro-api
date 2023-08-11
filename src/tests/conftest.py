import pytest
import pytest_asyncio
from httpx import AsyncClient

from app.api import endpoints
from app.api.security import create_unlimited_access_token
from app.main import app
from app.schemas import MediaUrl
from tests.db_utils import database as test_database
from tests.db_utils import reset_test_db


async def mock_hash_password(password):
    return f"hashed_{password}"


async def mock_verify_password(plain_password, hashed_password):
    return hashed_password == f"hashed_{plain_password}"


async def get_token(access_id, scopes):
    token_data = {"sub": str(access_id), "scopes": scopes}
    token = await create_unlimited_access_token(token_data)

    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def pytest_configure():
    # api.security patching
    pytest.mock_hash_password = mock_hash_password
    pytest.mock_verify_password = mock_verify_password
    pytest.get_token = get_token


@pytest_asyncio.fixture(scope="function")
async def test_app_asyncio():
    # for httpx>=20, follow_redirects=True (cf. https://github.com/encode/httpx/releases/tag/0.20.0)
    async with AsyncClient(app=app, base_url="http://test", follow_redirects=True) as ac:
        yield ac  # testing happens here


@pytest_asyncio.fixture(scope="function")
async def test_db():
    try:
        await test_database.connect()
        yield test_database
    finally:
        await reset_test_db()
        await test_database.disconnect()


@pytest.fixture(scope="function", autouse=True)
def patch_send_telegram_msg(monkeypatch):
    """Patch send_telegram_msg -> do nothing"""

    async def fake_send_telegram_msg(*arg, **kwargs):
        return None

    monkeypatch.setattr(endpoints.notifications, "send_telegram_msg", fake_send_telegram_msg)


@pytest.fixture(scope="function", autouse=True)
def patch_get_media_url(monkeypatch):
    """Patch get_media_url for notifications"""

    async def fake_get_media_url(*arg, **kwargs):
        return MediaUrl(url="https://avatars.githubusercontent.com/u/61667887?s=200&v=4")

    monkeypatch.setattr(endpoints.notifications, "get_media_url", fake_get_media_url)
