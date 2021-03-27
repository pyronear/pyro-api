# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
from app.api.routes import installations
from tests.db_utils import get_entry, fill_table
from tests.utils import update_only_datetime, parse_time

USER_TABLE = [
    {"id": 1, "login": "first_login", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_login", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

DEVICE_TABLE = [
    {"id": 1, "login": "third_login", "owner_id": 1,
     "access_id": 3, "specs": "v0.1", "elevation": None, "lat": None, "angle_of_view": 68.,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "fourth_login", "owner_id": 2, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68.,
     "created_at": "2020-10-13T08:18:45.447773"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "user"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scopes": "admin"},
    {"id": 3, "login": "third_login", "hashed_password": "hashed_pwd", "scopes": "device"},
    {"id": 4, "login": "fourth_login", "hashed_password": "hashed_pwd", "scopes": "device"},
]

SITE_TABLE = [
    {"id": 1, "name": "my_first_tower", "lat": 44.1, "lon": -0.7, "type": "tower", "country": "FR", "geocode": "40",
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "name": "my_first_station", "lat": 44.1, "lon": 3.9, "type": "station", "country": "FR", "geocode": "30",
     "created_at": "2020-09-13T08:18:45.447773"},
]

INSTALLATION_TABLE = [
    {"id": 1, "device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
     "start_ts": "2019-10-13T08:18:45.447773", "end_ts": None, "is_trustworthy": True,
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 2, "site_id": 2, "elevation": 58., "lat": 5., "lon": 8., "yaw": 10., "pitch": 0.,
     "start_ts": "2019-10-13T08:18:45.447773", "end_ts": None, "is_trustworthy": False,
     "created_at": "2020-11-13T08:18:45.447773"},
]

USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
SITE_TABLE_FOR_DB = list(map(update_only_datetime, SITE_TABLE))
INSTALLATION_TABLE_FOR_DB = list(map(update_only_datetime, INSTALLATION_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await fill_table(test_db, db.sites, SITE_TABLE_FOR_DB)
    await fill_table(test_db, db.installations, INSTALLATION_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "access_idx, installation_id, status_code, status_details",
    [
        [0, 1, 401, "Permission denied"],
        [1, 1, 200, None],
        [2, 1, 401, "Permission denied"],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_installation(test_app_asyncio, init_test_db,
                                access_idx, installation_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get(f"/installations/{installation_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == INSTALLATION_TABLE[installation_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [0, 401, "Permission denied"],
        [1, 200, None],
        [2, 401, "Permission denied"],
    ],
)
@pytest.mark.asyncio
async def test_fetch_installations(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get("/installations/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == INSTALLATION_TABLE


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [0, {"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-10-13T08:18:45.447773"},
         401, "Permission denied"],
        [1, {"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-10-13T08:18:45.447773"},
         201, None],
        [2, {"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-10-13T08:18:45.447773"},
         401, "Permission denied"],
        [1, {"device_id": 1, "site_id": 1, "elevation": "high", "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.},
         422, None],
        [1, {"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0.},
         422, None],
        [1, {"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "is_trustworthy": 5},
         422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_installation(test_app_asyncio, init_test_db, test_db,
                                   access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/installations/", data=json.dumps(payload), headers=auth)

    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        test_response = {"id": len(INSTALLATION_TABLE) + 1, **payload, "end_ts": None, "is_trustworthy": True}
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

        new_installation = await get_entry(test_db, db.installations, json_response["id"])
        new_installation = dict(**new_installation)

        # Timestamp consistency
        assert new_installation['created_at'] > utc_dt and new_installation['created_at'] < datetime.utcnow()
        # Check default value of is_trustworthy
        assert new_installation['is_trustworthy']


@pytest.mark.parametrize(
    "access_idx, payload, installation_id, status_code, status_details",
    [
        [0, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-07-13T08:18:45.447773"}, 1,
         401, "Permission denied"],
        [1, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-07-13T08:18:45.447773"}, 1,
         200, None],
        [2, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-07-13T08:18:45.447773"}, 1,
         401, "Permission denied"],
        [1, {}, 1, 422, None],
        [1, {"device_id": 1}, 1, 422, None],
        [1, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-07-13T08:18:45.447773"}, 999,
         404, "Entry not found"],
        [1, {"device_id": 1, "site_id": 1, "elevation": "high", "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-07-13T08:18:45.447773"}, 1,
         422, None],
        [1, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-07-13T08:18:45.447773", "is_trustworthy": 5.}, 1,
         422, None],
        [1, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
             "start_ts": "2020-07-13T08:18:45.447773"}, 0,
         422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_installation(test_app_asyncio, init_test_db, test_db,
                                   access_idx, payload, installation_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.put(f"/installations/{installation_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_installation = await get_entry(test_db, db.installations, installation_id)
        updated_installation = dict(**updated_installation)
        for k, v in updated_installation.items():
            if k == 'start_ts':
                assert v == parse_time(payload[k])
            else:
                assert v == payload.get(k, INSTALLATION_TABLE_FOR_DB[installation_id - 1][k])


@pytest.mark.parametrize(
    "access_idx, installation_id, status_code, status_details",
    [
        [0, 1, 401, "Permission denied"],
        [1, 1, 200, None],
        [2, 1, 401, "Permission denied"],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_installation(test_app_asyncio, init_test_db,
                                   access_idx, installation_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.delete(f"/installations/{installation_id}/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == INSTALLATION_TABLE[installation_id - 1]
        remaining_installations = await test_app_asyncio.get("/installations/", headers=auth)
        assert all(entry['id'] != installation_id for entry in remaining_installations.json())


@pytest.mark.parametrize(
    "access_idx, installation_id, device_ids, status_code, status_details",
    [
        [0, 1, [], 401, "Permission denied"],
        [1, 1, [1], 200, None],
        [2, 1, [], 401, "Permission denied"],
        [1, 999, [], 200, None],  # TODO: this should fail since the site doesn't exist
        [1, 0, [], 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_active_devices_on_site(test_app_asyncio, init_test_db, test_db, monkeypatch,
                                          access_idx, installation_id, device_ids, status_code, status_details):

    # Custom patching for DB operations done on route
    monkeypatch.setattr(installations, "database", test_db)

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get(f"/installations/site-devices/{installation_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == [DEVICE_TABLE[_id - 1]['id'] for _id in device_ids]
