# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
from tests.conf_test_db import get_entry_in_db, populate_db
from tests.utils import update_only_datetime

GROUP_TABLE = [
    {"id": 1, "name": "first_group", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "name": "second_group", "created_at": "2020-09-13T08:18:45.447773"}
]

def compare_entries(ref, test):
    for k, v in ref.items():
        if isinstance(v, float):
            # For float issues
            assert abs(v - test[k]) < 1E-5
        else:
            assert v == test[k]


GROUP_TABLE_FOR_DB = list(map(update_only_datetime, GROUP_TABLE))


async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.groups, GROUP_TABLE_FOR_DB)


@pytest.mark.asyncio
async def test_get_group(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/groups/1")
    response_json = response.json()
    assert response.status_code == 200
    compare_entries(response_json, GROUP_TABLE[0])


@pytest.mark.parametrize(
    "group_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_group_invalid(test_app_asyncio, test_db, monkeypatch, group_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get(f"/groups/{group_id}")
    assert response.status_code == status_code, group_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_groups(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/groups/")
    assert response.status_code == 200
    response_json = response.json()
    for (i, entry) in enumerate(response_json):
        compare_entries(entry, GROUP_TABLE[i])


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"names": "my_group"}, 422],
        [{}, 422],
    ],
)
@pytest.mark.asyncio
async def test_create_group_invalid(test_app_asyncio, test_db, payload, status_code):
    response = await test_app_asyncio.post("/groups/", data=json.dumps(payload))
    assert response.status_code == status_code


@pytest.mark.asyncio
async def test_update_group(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"name": "renamed_group"}
    response = await test_app_asyncio.put("/groups/1/", data=json.dumps(test_payload))
    print(response.json())
    assert response.status_code == 200
    updated_group_in_db = await get_entry_in_db(test_db, db.groups, 1)
    updated_group_in_db = dict(**updated_group_in_db)
    for k, v in updated_group_in_db.items():
        assert v == test_payload.get(k, GROUP_TABLE_FOR_DB[0][k])


@pytest.mark.parametrize(
    "group_id, payload, status_code",
    [
        [1, {}, 422],
        [999, {"name": "foo"}, 404],
        [1, {"name": "1"}, 422],
        [0, {"name": "foo"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_group_invalid(test_app_asyncio, test_db, monkeypatch, group_id, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)
    response = await test_app_asyncio.put(f"/groups/{group_id}/", data=json.dumps(payload))

    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_delete_group(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete("/groups/1/")
    assert response.status_code == 200
    compare_entries(response.json(), GROUP_TABLE[0])

    remaining_groups = await test_app_asyncio.get("/groups/")
    for entry in remaining_groups.json():
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "group_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_group_invalid(test_app_asyncio, test_db, monkeypatch, group_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete(f"/groups/{group_id}/")
    assert response.status_code == status_code, print(group_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(group_id)
