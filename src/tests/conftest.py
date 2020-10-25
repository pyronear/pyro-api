import pytest
from starlette.testclient import TestClient
from datetime import datetime as dt

from app.main import app
from app.api.schemas import UserOut, UserInDb
from app.api.deps import get_current_user


async def mock_current_user():
    return UserOut(id=99, username="connected_user", created_at=dt.now())


@pytest.fixture(scope="function")
def existing_users():
    return [
        UserInDb(id=1, username="first", created_at=dt.now(), hashed_password="first_hashed", scopes="me"),
        UserInDb(id=2, username="second", created_at=dt.now(), hashed_password="second_hashed", scopes="me"),
        UserInDb(id=3, username="third", created_at=dt.now(), hashed_password="third_hashed", scopes="me admin"),
    ]


@pytest.fixture(scope="module")
def test_app():

    app.dependency_overrides[get_current_user] = mock_current_user

    client = TestClient(app)
    yield client  # testing happens here

    print("Tests done.")
    app.dependency_overrides = {}
