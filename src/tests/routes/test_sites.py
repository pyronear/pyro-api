# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
from tests.db_utils import get_entry, fill_table, TestSessionLocal
from tests.utils import update_only_datetime


GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
    {"id": 2, "name": "second_group"}
]

SITE_TABLE = [
    {"id": 1, "name": "my_first_tower", "group_id": 1,
     "lat": 44.1, "lon": -0.7, "type": "tower", "country": "FR", "geocode": "40",
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "name": "my_first_station", "group_id": 2,
     "lat": 44.1, "lon": 3.9, "type": "station", "country": "FR", "geocode": "30",
     "created_at": "2020-09-13T08:18:45.447773"},
]

ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 1, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 2, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 2, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
]


def compare_entries(ref, test):
    for k, v in ref.items():
        if isinstance(v, float):
            # For float issues
            assert abs(v - test[k]) < 1E-5
        else:
            assert v == test[k]


SITE_TABLE_FOR_DB = list(map(update_only_datetime, SITE_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(db, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.sites, SITE_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [1, 200, None],
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_site(test_app_asyncio, init_test_db, site_id, status_code, status_details):

    response = await test_app_asyncio.get(f"/sites/{site_id}")
    response_json = response.json()
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code == 200:
        compare_entries(response_json, SITE_TABLE[site_id - 1])


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_sites",
    [
        [0, 200, None, [SITE_TABLE[0]]],
        [1, 200, None, SITE_TABLE],
        [2, 401, "Permission denied", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_sites(test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_sites):
    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/sites/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:

        for (i, entry) in enumerate(response.json()):
            compare_entries(entry, expected_sites[i])


@pytest.mark.parametrize(
    "access_idx, payload, no_alert, status_code, status_details",
    [
        [1, {"name": "my_site", "group_id": 1, "lat": 0., "lon": 0.,
             "type": "tower", "country": "FR", "geocode": "01"}, False,
         201, None],
        [1, {"name": "my_site", "group_id": 1, "lat": 0., "lon": 0.,
             "type": "station", "country": "FR", "geocode": "01"}, False,
         201, None],
        [1, {"name": "my_site", "group_id": 1, "lat": 0., "lon": 0.,
             "country": "FR", "geocode": "01"}, True, 201, None],
        [0, {"name": "my_site", "group_id": 1, "lat": 0., "lon": 0.,
             "country": "FR", "geocode": "01"}, False,
         401, "Permission denied"],
        [0, {"name": "my_site", "group_id": 1, "lat": 0., "lon": 0.,
             "country": "FR", "geocode": "01"}, True, 201, None],
        [2, {"name": "my_site", "group_id": 1, "lat": 0., "lon": 0.,
             "country": "FR", "geocode": "01"}, False,
         401, "Permission denied"],
        [1, {"names": "my_site", "group_id": 1, "lat": 0., "lon": 0.,
             "country": "FR", "geocode": "01"}, False, 422, None],
        [1, {"name": "my_site", "group_id": 1, "lat": 0.,
             "country": "FR", "geocode": "01"}, False, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_site(test_app_asyncio, init_test_db, test_db,
                           access_idx, payload, no_alert, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    test_response = {"id": len(SITE_TABLE) + 1, **payload}
    subroute = ""
    if no_alert:
        test_response['type'] = 'no_alert'
        subroute = "/no-alert"

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post(f"/sites{subroute}/", data=json.dumps(payload), headers=auth)

    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
        new_site_in_db = await get_entry(test_db, db.sites, json_response["id"])
        new_site_in_db = dict(**new_site_in_db)
        assert new_site_in_db['created_at'] > utc_dt and new_site_in_db['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, site_id, status_code, status_details",
    [
        [1, {"name": "renamed_site", "lat": 0., "lon": 0., "country": "FR", "geocode": "01"}, 1, 200, None],
        [0, {"name": "renamed_site", "lat": 0., "lon": 0., "country": "FR", "geocode": "01"}, 1,
         401, "Permission denied"],
        [1, {}, 1, 422, None],
        [1, {"site_name": "foo"}, 1, 422, None],
        [1, {"name": "foo", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}, 999, 404, None],
        [1, {"name": "1", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}, 1, 422, None],
        [1, {"name": "foo", "lat": 0., "lon": 0., "type": "tower", "country": "FR", "geocode": "01"}, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_site(test_app_asyncio, init_test_db, test_db,
                           access_idx, payload, site_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/sites/{site_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_site_in_db = await get_entry(test_db, db.sites, site_id)
        updated_site_in_db = dict(**updated_site_in_db)
        for k, v in updated_site_in_db.items():
            assert v == payload.get(k, SITE_TABLE_FOR_DB[site_id - 1][k])


@pytest.mark.parametrize(
    "access_idx, site_id, status_code, status_details",
    [
        [1, 1, 200, None],
        [0, 1, 401, "Permission denied"],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_site(test_app_asyncio, init_test_db, access_idx, site_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.delete(f"/sites/{site_id}/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        compare_entries(response.json(), SITE_TABLE[site_id - 1])
        remaining_sites = await test_app_asyncio.get("/sites/", headers=auth)
        assert all(entry['id'] != site_id for entry in remaining_sites.json())
