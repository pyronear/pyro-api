# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import json
import pytest
from datetime import datetime

from app import db
from app.api import crud
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

MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]


EVENT_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": "2021-03-13T10:18:45.447773",
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "lat": 6., "lon": 8., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-09-13T08:18:45.447773"},
    {"id": 3, "lat": -5., "lon": 3., "type": "wildfire", "start_ts": "2021-03-13T08:18:45.447773",
     "end_ts": "2021-03-13T10:18:45.447773", "created_at": "2020-09-13T08:18:45.447773"},
]

ALERT_TABLE = [
    {"id": 1, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": None, "is_acknowledged": True, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0.,
     "azimuth": 47., "is_acknowledged": True, "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 3, "device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8.,
     "azimuth": 123., "is_acknowledged": False, "created_at": "2020-11-03T11:18:45.447773"},
]

USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
MEDIA_TABLE_FOR_DB = list(map(update_only_datetime, MEDIA_TABLE))
EVENT_TABLE_FOR_DB = list(map(update_only_datetime, EVENT_TABLE))
ALERT_TABLE_FOR_DB = list(map(update_only_datetime, ALERT_TABLE))


@pytest.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)
    await fill_table(test_db, db.users, USER_TABLE_FOR_DB)
    await fill_table(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await fill_table(test_db, db.media, MEDIA_TABLE_FOR_DB)
    await fill_table(test_db, db.events, EVENT_TABLE_FOR_DB)
    await fill_table(test_db, db.alerts, ALERT_TABLE_FOR_DB)


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
async def test_get_alert(test_app_asyncio, init_test_db, access_idx, alert_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get(f"/alerts/{alert_id}", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        response_json = response.json()
        response_json["created_at"] = parse_time(response_json["created_at"])
        assert response_json == ALERT_TABLE_FOR_DB[alert_id - 1]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [0, 401, "Permission denied"],
        [1, 200, None],
        [2, 401, "Permission denied"],
    ],
)
@pytest.mark.asyncio
async def test_fetch_alerts(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get("/alerts/", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == ALERT_TABLE


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [0, 401, "Permission denied"],
        [1, 200, None],
        [2, 401, "Permission denied"],
    ],
)
@pytest.mark.asyncio
async def test_fetch_ongoing_alerts(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get("/alerts/ongoing", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == ALERT_TABLE[:2]


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [0, 401, "Permission denied"],
        [1, 200, None],
        [2, 401, "Permission denied"],
    ],
)
@pytest.mark.asyncio
async def test_fetch_unacknowledged_alerts(test_app_asyncio, init_test_db, access_idx, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.get("/alerts/unacknowledged", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        assert response.json() == [x for x in ALERT_TABLE if x["is_acknowledged"] is False]


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [0, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": 47.5},
         401, "Permission denied"],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": 47.5}, 201, None],
        [2, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": 47.5},
         401, "Permission denied"],
        [1, {"event_id": 2, "lat": 10., "lon": 8.}, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": "hello"}, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "azimuth": -5.}, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_create_alert(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/alerts/", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        json_response = response.json()
        test_response = {"id": len(ALERT_TABLE) + 1, **payload,
                         "media_id": None, "is_acknowledged": False}
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

        new_alert = await get_entry(test_db, db.alerts, json_response["id"])
        new_alert = dict(**new_alert)
        assert new_alert['created_at'] > utc_dt and new_alert['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, status_code, status_details",
    [
        [0, {"event_id": 2, "lat": 10., "lon": 8.}, 401, "Permission denied"],
        [1, {"event_id": 2, "lat": 10., "lon": 8.}, 401, "Permission denied"],
        [2, {"event_id": 2, "lat": 10., "lon": 8.}, 201, None],
    ],
)
@pytest.mark.asyncio
async def test_create_alert_by_device(test_app_asyncio, init_test_db, test_db,
                                      access_idx, payload, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

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
        test_response = {"id": len(ALERT_TABLE) + 1,
                         "device_id": device_id, **payload,
                         "media_id": None, "is_acknowledged": False, "azimuth": None}
        assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
        new_alert = await get_entry(test_db, db.alerts, json_response["id"])
        new_alert = dict(**new_alert)
        assert new_alert['created_at'] > utc_dt and new_alert['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "access_idx, payload, alert_id, status_code, status_details",
    [
        [0, {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8.}, 1, 401, "Permission denied"],
        [1, {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8.}, 1, 200, None],
        [2, {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8.}, 1, 401, "Permission denied"],
        [1, {}, 1, 422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "is_acknowledged": True}, 999,
         404, "Entry not found"],
        [1, {"device_id": 2, "lat": 10., "lon": 8., "is_acknowledged": True}, 1,
         422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "is_acknowledged": True}, 0,
         422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "is_acknowledged": True,
             "azimuth": "north"}, 1,
         422, None],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "is_acknowledged": True,
             "azimuth": -5.}, 1,
         422, None],
    ],
)
@pytest.mark.asyncio
async def test_update_alert(test_app_asyncio, init_test_db, test_db,
                            access_idx, payload, alert_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

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
    ],
)
@pytest.mark.asyncio
async def test_acknowledge_alert(test_app_asyncio, init_test_db, test_db,
                                 access_idx, alert_id, status_code, status_details):

    # Create a custom access token
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

    response = await test_app_asyncio.put(f"/alerts/{alert_id}/acknowledge", headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_alert = await get_entry(test_db, db.alerts, alert_id)
        updated_alert = dict(**updated_alert)
        assert updated_alert['is_acknowledged']


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
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())

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
    auth = await pytest.get_token(ACCESS_TABLE[access_idx]['id'], ACCESS_TABLE[access_idx]['scopes'].split())
    response = await test_app_asyncio.put(f"/alerts/{alert_id}/link-media", data=json.dumps(payload), headers=auth)
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()['detail'] == status_details

    if response.status_code // 100 == 2:
        updated_entry = await get_entry(test_db, db.alerts, alert_id)
        updated_entry = dict(**updated_entry)
        assert updated_entry['media_id'] == payload['media_id'], print(payload, updated_entry)
