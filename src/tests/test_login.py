import pytest

from app import db
from app.api import crud, security
from tests.conf_test_db import populate_db

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "first_pwd_hashed", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "second_pwd_hashed", "scopes": "me"},
]


@pytest.mark.parametrize(
    "payload, status_code, status_detail",
    [
        [{"username": "foo"}, 422, None],
        [{"password": "foo"}, 422, None],
        [{"username": "unknown", "password": "foo"}, 400, "Invalid credentials"],  # unknown username
        [{"username": "first", "password": "second"}, 400, "Invalid credentials"],  # wrong pwd
        [{"username": "first_login", "password": "first_pwd"}, 200, None],  # valid
    ],
)
@pytest.mark.asyncio
async def test_create_access_token(test_app_asyncio, test_db, monkeypatch, payload, status_code, status_detail):

    # Sterilize DB interactions
    monkeypatch.setattr(security, "verify_password", pytest.mock_verify_password)
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.post("/login/access-token", data=payload)

    assert response.status_code == status_code, print(payload)
    if isinstance(status_detail, str):
        assert response.json()['detail'] == status_detail
