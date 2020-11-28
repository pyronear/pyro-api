import pytest
from starlette.testclient import TestClient
from datetime import datetime

from app.main import app
from app.api.schemas import UserRead, DeviceOut
from app.api.deps import get_current_user, get_current_device
from tests.conf_test_db import database as test_database
from tests.conf_test_db import reset_test_db
from httpx import AsyncClient


async def mock_current_user():
    return UserRead(id=2, login="connected_user", created_at=datetime.now())


async def mock_current_device():
    return DeviceOut(id=1, owner_id=1, specs="raspberry", login="connected_device", created_at=datetime.now())


async def mock_hash_password(password):
    return f"{password}_hashed"


async def mock_verify_password(plain_password, hashed_password):
    return hashed_password == f"{plain_password}_hashed"


def pytest_configure():
    # CRUD patching
    pytest.mock_hash_password = mock_hash_password
    pytest.mock_verify_password = mock_verify_password


@pytest.fixture(scope="module")
def __app():

    # Access-related patching
    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[get_current_device] = mock_current_device

    yield app  # testing happens here

    app.dependency_overrides = {}


@pytest.fixture(scope="module")
def test_app(__app):
    client = TestClient(__app)
    yield client  # testing happens here


@pytest.fixture(scope="function")
async def test_app_asyncio(__app):
    async with AsyncClient(app=__app, base_url="http://test") as ac:
        yield ac  # testing happens here


@pytest.fixture(scope="function")
async def test_db():
    try:
        await test_database.connect()
        yield test_database
    finally:
        print("Clean the DB")
        await reset_test_db()
        await test_database.disconnect()
