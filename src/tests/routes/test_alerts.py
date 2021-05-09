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


DEVICE_TABLE = [
    {"id": 1, "login": "third_login", "owner_id": 1,
     "access_id": 3, "specs": "v0.1", "elevation": None, "lat": None, "angle_of_view": 68., "software_hash": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "fourth_login", "owner_id": 2, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "angle_of_view": 68., "software_hash": None,
     "created_at": "2020-10-13T08:18:45.447773"},
]

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
    {"id": 2, "name": "second_group"}
]

ACCESS_TABLE = [
    {"id": 1, "group_id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user"},
    {"id": 2, "group_id": 1, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin"},
    {"id": 3, "group_id": 1, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 4, "group_id": 2, "login": "fourth_login", "hashed_password": "hashed_pwd", "scope": "device"},
    {"id": 5, "group_id": 2, "login": "fifth_login", "hashed_password": "hashed_pwd", "scope": "user"},
]

MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]


EVENT_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": "2021-03-13T10:18:45.447773",
     "is_acknowledged": True, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "lat": 6., "lon": 8., "type": "wildfire", "start_ts": None, "end_ts": None,
     "is_acknowledged": True, "created_at": "2020-09-13T08:18:45.447773"},
    {"id": 3, "lat": -5., "lon": 3., "type": "wildfire", "start_ts": "2021-03-13T08:18:45.447773",
     "end_ts": None, "is_acknowledged": False, "created_at": "2020-09-13T08:18:45.447773"},
]

ALERT_TABLE = [
    {"id": 1, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": 47., "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 3, "device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8.,
     "azimuth": 123., "created_at": "2020-11-03T11:18:45.447773"},
    {"id": 4, "device_id": 1, "event_id": 3, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": 47., "created_at": ts_to_string(datetime.utcnow())},
]

USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
MEDIA_TABLE_FOR_DB = list(map(update_only_datetime, MEDIA_TABLE))
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
    await fill_table(test_db, db.media, MEDIA_TABLE_FOR_DB)
    await fill_table(test_db, db.events, EVENT_TABLE_FOR_DB)
    await fill_table(test_db, db.alerts, ALERT_TABLE_FOR_DB)


@pytest.mark.parametrize(
    "access_idx, alert_id, status_code, status_details",
    [
        [0, 1, 200, None],
        [1, 1, 200, None],
        [2, 1, 401, "Permission denied"],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
        [4, 1, 401, "You can't access this ressource"],
    ],
)
@pytest.mark.asyncio
async def test_get_alert(test_app_asyncio, init_test_db, access_idx, alert_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get(f"/alerts/{alert_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        response_json = response.json()
        response_json["created_at"] = parse_time(response_json["created_at"])
        assert response_json == ALERT_TABLE_FOR_DB[alert_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details, expected_results",
    [
        [0, 200, None, [ALERT_TABLE[0], ALERT_TABLE[1], ALERT_TABLE[3]]],
        [1, 200, None, ALERT_TABLE],
        [2, 401, "Permission denied", None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_alerts(test_app_asyncio, init_test_db, access_idx, status_code,
                            status_details, expected_results):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/alerts/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == expected_results


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
async def test_fetch_ongoing_alerts(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.get("/alerts/ongoing", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        event_ids = [entry['id'] for entry in EVENT_TABLE if entry['end_ts'] is None]

        alerts_group_id = [entry["id"] for entry in ALERT_TABLE]

        # Retrieve group_id condition first
        if ACCESS_TABLE[access_idx]["scope"] != "admin":
            group_id = ACCESS_TABLE[access_idx]["group_id"]
            access_group_id = [access["id"] for access in ACCESS_TABLE if access["group_id"] == group_id]
            devices_group_id = [device["id"] for device in DEVICE_TABLE if device["access_id"] in access_group_id]
            alerts_group_id = [alert["id"] for alert in ALERT_TABLE if alert["device_id"] in devices_group_id]

        assert response.json() == [entry for entry in ALERT_TABLE if (
            entry['event_id'] in event_ids and entry["id"] in alerts_group_id)]


@pytest.mark.parametrize(
    "access_idx, payload, expected_event_id, status_code, status_details",
    [
        [0, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": 47.5}, None,
         401, "Permission denied"],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": 47.5}, None, 201, None],
        [1, {"device_id": 2, "lat": 10., "lon": 8., "azimuth": 47.5}, 4, 201, None],
        [1, {"device_id": 1, "lat": 10., "lon": 8., "azimuth": 47.5}, 3, 201, None],
        [2, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": 47.5}, None,
         401, "Permission denied"],
        [1, {"event_id": 2, "lat": 10., "lon": 8.}, None, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": "hello"}, None, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": -5.}, None, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_alert(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, expected_event_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/alerts/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        test_response = {"id": len(ALERT_TABLE) + 1, **payload, "media_id": None}
        if isinstance(expected_event_id, int):
            test_response['event_id'] = expected_event_id
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

        new_alert = await get_entry(test_db, db.alerts, json_response["id"])
        new_alert = dict(**new_alert)
        assert new_alert['created_at'] > utc_dt and new_alert['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, expected_event_id, status_code, status_details",
    [
        [0, {"event_id": 2, "lat": 10., "lon": 8.}, None, 401, "Permission denied"],
        [1, {"event_id": 2, "lat": 10., "lon": 8.}, None, 401, "Permission denied"],
        [2, {"event_id": 2, "lat": 10., "lon": 8.}, None, 201, None],
        [2, {"lat": 10., "lon": 8.}, 3, 201, None],
        [3, {"lat": 10., "lon": 8.}, 4, 201, None],
    ],
)
@pytest.mark.asyncio
async def test_create_alert_by_device(test_app_asyncio, init_test_db, test_db,
                                      access_idx, payload, expected_event_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/alerts/from-device", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        device_id = None
        for entry in DEVICE_TABLE:
            if entry['access_id'] == ACCESS_TABLE[access_idx]['id']:
                device_id = entry['id']
                break
        # Device_id is 99 because it is the identified device
        test_response = {"id": len(ALERT_TABLE) + 1, "device_id": device_id, **payload,
                         "media_id": None, "azimuth": None}
        if isinstance(expected_event_id, int):
            test_response['event_id'] = expected_event_id
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
        new_alert = await get_entry(test_db, db.alerts, json_response["id"])
        new_alert = dict(**new_alert)
        assert new_alert['created_at'] > utc_dt and new_alert['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, alert_id, status_code, status_details",
    [
        [0, {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8.}, 1, 200, None],
        [1, {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8.}, 1, 200, None],
        [2, {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8.}, 1, 401, "Permission denied"],
        [1, {}, 1, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8.}, 999, 404, "Entry not found"],
        [1, {"device_id": 2, "lat": 10.}, 1, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8.}, 0, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": "north"}, 1, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": -5.}, 1, 422, None],
        [4, {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8.}, 1, 401, "You can't specify another group"],

    ],
)
@pytest.mark.asyncio
async def test_update_alert(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, alert_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.put(f"/alerts/{alert_id}/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_alert = await get_entry(test_db, db.alerts, alert_id)
        updated_alert = dict(**updated_alert)
        assert all(updated_alert[k] == v for k, v in payload.items())


@pytest.mark.parametrize(
    "access_idx, alert_id, status_code, status_details",
    [
        [0, 1, 401, "Permission denied"],
        [1, 1, 200, None],
        [2, 1, 401, "Permission denied"],
        [1, 999, 404, "Entry not found"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_alert(test_app_asyncio, init_test_db, access_idx, alert_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())

    response = await test_app_asyncio.delete(f"/alerts/{alert_id}/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == ALERT_TABLE[alert_id - 1]
        remaining_alerts = await test_app_asyncio.get("/alerts/", headers=auth)
        assert all(entry['id'] != alert_id for entry in remaining_alerts.json())


@pytest.mark.parametrize(
    "access_idx, payload, alert_id, status_code, status_details",
    [
        [0, {"media_id": 1}, 1, 401, "Permission denied"],
        [1, {"media_id": 1}, 1, 401, "Permission denied"],
        [2, {"media_id": 1}, 1, 200, None],
        [2, {"media_id": 1}, 3, 401, "Permission denied"],
        [2, {"media_id": 100}, 1, 404, "Media does not exist"],
    ],
)
@pytest.mark.asyncio
async def test_link_media(test_app_asyncio, init_test_db, test_db,
                          access_idx, payload, alert_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scope'].split())
    response = await test_app_asyncio.put(f"/alerts/{alert_id}/link-media", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_entry = await get_entry(test_db, db.alerts, alert_id)
        updated_entry = dict(**updated_entry)
        assert updated_entry['media_id'] == payload['media_id'], print(payload, updated_entry)
