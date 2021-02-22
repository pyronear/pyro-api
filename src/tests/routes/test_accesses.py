# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import pytest

from app import db
from app.api import crud
from tests.conf_test_db import populate_db

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scopes": "me"},
]


@pytest.mark.asyncio
async def test_get_access(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.get("/accesses/1")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in ACCESS_TABLE[0].items() if k != "hashed_password"}


@pytest.mark.parametrize(
    "access_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_access_invalid(test_app_asyncio, test_db, monkeypatch, access_id, status_code, status_details):
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.get(f"/accesses/{access_id}")
    assert response.status_code == status_code, access_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_accesses(test_app_asyncio, test_db, monkeypatch):
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)

    response = await test_app_asyncio.get("/accesses/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "hashed_password"}
                               for entry in ACCESS_TABLE]
