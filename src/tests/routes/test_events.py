# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
from tests.db_utils import get_entry, fill_table, TestSessionLocal
from tests.utils import update_only_datetime, parse_time, ts_to_string


USER_TABLE = [
    {"id": 1, "login": "first_login", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_login", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
    {"id": 3, "login": "fifth_login", "access_id": 5, "created_at": "2020-11-13T08:18:45.447773"},
]

EVENT_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": "2020-09-13T08:18:45.447773",
     "end_ts": "2020-09-13T08:18:45.447773", "is_acknowledged": True, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "lat": 6., "lon": 8., "type": "wildfire", "start_ts": None, "end_ts": None,
     "is_acknowledged": True, "created_at": "2020-09-13T08:18:45.447773"},
    {"id": 3, "lat": -5., "lon": 3., "type": "wildfire", "start_ts": "2021-03-13T08:18:45.447773",
     "end_ts": "2021-03-13T10:18:45.447773", "is_acknowledged": False, "created_at": "2020-09-13T08:18:45.447773"},
]

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
    {"id": 2, "name": "second_group"}
]

DEVICE_TABLE = [
    {"id": 1, "login": "third_login", "owner_id": 1,
     "access_id": 3, "specs": "v0.1", "elevation": None, "lat": None, "angle_of_view": 68., "software_hash": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "fourth_login", "owner_id": 2, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68., "software_hash": None,
     "created_at": "2020-10-13T08:18:45.447773"},
]

ALERT_TABLE = [
    {"id": 1, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "event_id": 2, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": 47., "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 3, "device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8.,
     "azimuth": 123., "created_at": "2020-11-03T11:18:45.447773"},
    {"id": 4, "device_id": 2, "event_id": 3, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": 47., "created_at": ts_to_string(datetime.utcnow())},
]

ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 1, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 1, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 2, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 5, "group_id": 2, "login": "fifth_login", "hashed_password": "hashed_pwd", "scope": "user"},
]

USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
EVENT_TABLE_FOR_DB = list(map(update_only_datetime, EVENT_TABLE))
ALERT_TABLE_FOR_DB = list(map(update_only_datetime, ALERT_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    monkeypatch.setattr(db, "SessionLocal", TestSessionLocal)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await fill_table(test_db, db.events, EVENT_TABLE_FOR_DB)
    await fill_table(test_db, db.alerts, ALERT_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "access_idx, event_id, status_code, status_details",
    [
        [0, 1, 200, None],
        [1, 1, 200, None],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
        [4, 1, 401, None],
    ],
)
@pytest.mark.asyncio
async def test_get_event(test_app_asyncio, init_test_db, access_idx, event_id, status_code, status_details):
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get(f"/events/{event_id}", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == EVENT_TABLE[event_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_results",
    [
        [0, 200, None, [EVENT_TABLE[0], EVENT_TABLE[1]]],
        [1, 200, None, EVENT_TABLE],
        [2, 401, "Permission denied", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_events(test_app_asyncio, init_test_db, access_idx, status_code, status_details, expected_results):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/events/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_results


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_results",
    [
        [0, 200, None, [EVENT_TABLE[0]]],
        [1, 200, None, [entry for entry in EVENT_TABLE if entry["end_ts"] is not None]],
        [2, 401, "Permission denied", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_past_events(test_app_asyncio, init_test_db,
                                 access_idx, status_code, status_details, expected_results):
    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/events/past", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_results


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
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/events/", data=json.dumps(payload), headers=auth)

    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        json_response = response.json()
        test_response = {"id": len(EVENT_TABLE) + 1, **payload, "is_acknowledged": False}
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
        new_event_in_db = await get_entry(test_db, db.events, json_response["id"])
        new_event_in_db = dict(**new_event_in_db)
        assert new_event_in_db['created_at'] > utc_dt and new_event_in_db['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, event_id, status_code, status_details",
    [
        [0, {"lat": 5., "lon": 10., "type": "wildfire", "is_acknowledged": True}, 1, 401, "Permission denied"],
        [1, {"lat": 5., "lon": 10., "type": "wildfire", "is_acknowledged": True}, 1, 200, None],
        [2, {"lat": 5., "lon": 10., "type": "wildfire", "is_acknowledged": True}, 1, 200, None],
        [1, {}, 1, 422, None],
        [1, {"type": "wildfire"}, 1, 422, None],
        [1, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 999, 404, "Entry not found"],
        [1, {"lat": 0., "lon": 0., "type": "lightning", "start_ts": None, "end_ts": None}, 1, 422, None],
        [1, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": "now", "end_ts": None}, 1, 422, None],
        [1, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None}, 0, 422, None],
        [3, {"lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None},
         1, 401, "You can't specify another group"],
    ],
)
@pytest.mark.asyncio
async def test_update_event(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, event_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/events/{event_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_event_in_db = await get_entry(test_db, db.events, event_id)
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
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.delete(f"/events/{event_id}/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details
    if response.status_code // 100 == 2:
        assert response.json() == EVENT_TABLE[event_id - 1]
        remaining_events = await test_app_asyncio.get("/events/", headers=auth)
        assert all(entry['id'] != event_id for entry in remaining_events.json())


@pytest.mark.parametrize(
    "access_idx, event_id, status_code, status_details",
    [
        [0, 1, 200, None],
        [1, 1, 200, None],
        [2, 1, 401, "Permission denied"],
    ],
)
@pytest.mark.asyncio
async def test_acknowledge_event(test_app_asyncio, init_test_db, test_db,
                                 access_idx, event_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/events/{event_id}/acknowledge", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_event = await get_entry(test_db, db.events, event_id)
        updated_event = dict(**updated_event)
        assert updated_event['is_acknowledged']


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [0, 200, None],
        [1, 200, None],
        [2, 401, "Permission denied"],
        [4, 200, None]
    ],
)
@pytest.mark.asyncio
async def test_fetch_unacknowledged_events(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/events/unacknowledged", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        events_group_id = [entry["id"] for entry in EVENT_TABLE]

        # Retrieve group_id condition first
        if ACCESS_TABLE[access_idx]["scope"] != "admin":
            group_id = ACCESS_TABLE[access_idx]["group_id"]
            access_group_id = [access["id"] for access in ACCESS_TABLE if access["group_id"] == group_id]
            devices_group_id = [device["id"] for device in DEVICE_TABLE if device["access_id"] in access_group_id]
            event_ids = [alert["event_id"] for alert in ALERT_TABLE if alert["device_id"] in devices_group_id]
            events_group_id = [event["id"] for event in EVENT_TABLE if event["id"] in event_ids]

        assert response.json() == [x for x in EVENT_TABLE if x["is_acknowledged"] is False
                                   and x["id"] in events_group_id]
