import pytest
from starlette.testclient import TestClient
from datetime import datetime as dt

from app.main import app
from app.api.schemas import UserRead
from app.api.deps import get_current_user


async def mock_current_user():
    return UserRead(id=99, username="connected_user", created_at=dt.now())


@pytest.fixture(scope="module")
def test_app():

    app.dependency_overrides[get_current_user] = mock_current_user

    client = TestClient(app)
    yield client  # testing happens here

    app.dependency_overrides = {}
