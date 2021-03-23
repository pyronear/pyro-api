# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
from tests.db_utils import get_entry_in_db, populate_db
from tests.utils import update_only_datetime


EVENT_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "lat": 6., "lon": 8., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-09-13T08:18:45.447773"},
    {"id": 3, "lat": -5., "lon": 3., "type": "wildfire", "start_ts": "2021-03-13T08:18:45.447773",
     "end_ts": "2021-03-13T10:18:45.447773", "created_at": "2020-09-13T08:18:45.447773"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "user"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scopes": "admin"},
    {"id": 3, "login": "third_login", "hashed_password": "hashed_pwd", "scopes": "device"},
]


EVENT_TABLE_FOR_DB = list(map(update_only_datetime, EVENT_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE)
    await populate_db(test_db, db.events, EVENT_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "event_id, status_code, status_details",
    [
        [1, 200, None],
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_event(test_app_asyncio, init_test_db, event_id, status_code, status_details):

    response = await test_app_asyncio.get(f"/events/{event_id}")
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == EVENT_TABLE[event_id - 1]


@pytest.mark.asyncio
async def test_fetch_events(test_app_asyncio, init_test_db):

    response = await test_app_asyncio.get("/events/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in EVENT_TABLE]


@pytest.mark.asyncio
async def test_fetch_past_events(test_app_asyncio, init_test_db):

    response = await test_app_asyncio.get("/events/past")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"}
                               for entry in EVENT_TABLE if entry['end_ts'] is not None]


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [0, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 401, "Permission denied"],
        [1, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 201, None],
        [2, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 201, None],
        [1, {"lat": 0., "lon": 0., "type": "lightning", "start_ts": None, "end_ts": None}, 422, None],
        [2, {"lat": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_event(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    test_response = {"id": len(EVENT_TABLE) + 1, **payload}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/events/", data=json.dumps(payload), headers=auth)

    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        json_response = response.json()
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
        new_event_in_db = await get_entry_in_db(test_db, db.events, json_response["id"])
        new_event_in_db = dict(**new_event_in_db)
        assert new_event_in_db['created_at'] > utc_dt and new_event_in_db['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, event_id, status_code, status_details",
    [
        [0, {"lat": 5., "lon": 10., "type": "wildfire"}, 1, 401, "Permission denied"],
        [1, {"lat": 5., "lon": 10., "type": "wildfire"}, 1, 200, None],
        [2, {"lat": 5., "lon": 10., "type": "wildfire"}, 1, 200, None],
        [1, {}, 1, 422, None],
        [1, {"type": "wildfire"}, 1, 422, None],
        [1, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 999, 404, "Entry not found"],
        [1, {"lat": 0., "lon": 0., "type": "lightning", "start_ts": None, "end_ts": None}, 1, 422, None],
        [1, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": "now", "end_ts": None}, 1, 422, None],
        [1, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_event(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, event_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.put(f"/events/{event_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_event_in_db = await get_entry_in_db(test_db, db.events, event_id)
        updated_event_in_db = dict(**updated_event_in_db)
        for k, v in updated_event_in_db.items():
            assert v == payload.get(k, EVENT_TABLE_FOR_DB[event_id - 1][k])


@pytest.mark.parametrize(
    "access_idx, event_id, status_code, status_details",
    [
        [0, 1, 401, "Permission denied"],
        [1, 1, 200, None],
        [2, 1, 401, "Permission denied"],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_event(test_app_asyncio, init_test_db, access_idx, event_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.delete(f"/events/{event_id}/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == EVENT_TABLE[event_id - 1]
        remaining_events = await test_app_asyncio.get("/events/")
        assert all(entry['id'] != event_id for entry in remaining_events.json())
