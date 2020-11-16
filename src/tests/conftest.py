import pytest
from starlette.testclient import TestClient
from datetime import datetime as dt

from app.main import app
from app.api.schemas import UserRead, DeviceOut
from app.api.deps import get_current_user, get_current_device, get_current_access


async def mock_current_user():
    return UserRead(id=99, username="connected_user", created_at=dt.now())


async def mock_current_device():
    return DeviceOut(id=99, owner_id=1, specs="raspberry", name="connected_device", created_at=dt.now())


@pytest.fixture(scope="module")
def test_app():

    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[get_current_device] = mock_current_device

    client = TestClient(app)
    yield client  # testing happens here

    app.dependency_overrides = {}
