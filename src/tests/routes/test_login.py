# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import pytest

from app import db
from app.api import crud, security
from tests.db_utils import fill_table

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_first_pwd", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_second_pwd", "scopes": "me"},
]


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(security, "verify_password", pytest.mock_verify_password)
    monkeypatch.setattr(crud.base, "database", test_db)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)


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
async def test_create_access_token(test_app_asyncio, init_test_db, payload, status_code, status_detail):

    response = await test_app_asyncio.post("/login/access-token", data=payload)

    assert response.status_code == status_code, print(payload)
    if isinstance(status_detail, str):
        assert response.json()['detail'] == status_detail
