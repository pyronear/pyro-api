# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import pytest

from app import db
from app.api import crud
from tests.db_utils import fill_table


ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "user"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scopes": "admin"},
    {"id": 3, "login": "third_login", "hashed_password": "hashed_pwd", "scopes": "device"},
]


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)


@pytest.mark.parametrize(
    "access_idx, access_id, status_code, status_details",
    [
        [0, 1, 401, "Permission denied"],
        [0, 2, 401, "Permission denied"],
        [1, 1, 200, None],
        [1, 2, 200, None],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_access(init_test_db, test_app_asyncio, access_idx, access_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get(f"/accesses/{access_id}", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code == 200:
        access = None
        for _access in ACCESS_TABLE:
            if _access['id'] == access_id:
                access = _access
                break
        assert response.json() == {k: v for k, v in access.items() if k != "hashed_password"}


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [0, 401, "Permission denied"],
        [1, 200, None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_accesses(init_test_db, test_app_asyncio, access_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get("/accesses/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code == 200:
        assert response.json() == [{k: v for k, v in entry.items() if k != "hashed_password"}
                                   for entry in ACCESS_TABLE]
