import json
import pytest
from copy import deepcopy
from datetime import datetime

from app import db
from app.api import crud
from tests.conf_test_db import get_entry_in_db, populate_db
from tests.utils import update_only_datetime, parse_time

MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]

ACCESS_TABLE = [{"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "me"},
                {"id": 2, "login": "first_device", "hashed_password": "hashed_pwd", "scopes": "device"},
                {"id": 3, "login": "second_device", "hashed_password": "hashed_pwd", "scopes": "device"}]

USER_TABLE = [{"id": 1, "login": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"}]


DEVICE_TABLE = [{
                "id": 1, "login": "first_device", "owner_id": 1, "access_id": 2,
                "specs": "v0.1", "elevation": None, "lat": None,
                "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
                {"id": 2, "login": "second_device", "owner_id": 1, "access_id": 3,
                 "specs": "v0.1", "elevation": None, "lat": None,
                 "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"}
                ]

EVENT_TABLE = [
    {"id": 1, "lat": 0., "lon": 0., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "lat": 6., "lon": 8., "type": "wildfire", "start_ts": None, "end_ts": None,
     "created_at": "2020-09-13T08:18:45.447773"},
]

ALERT_TABLE = [
    {"id": 1, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0., "type": "start",
     "is_acknowledged": True, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "event_id": 1, "media_id": None, "lat": 0., "lon": 0., "type": "end",
     "is_acknowledged": True, "created_at": "2020-10-13T09:18:45.447773"},
    {"id": 3, "device_id": 2, "event_id": 2, "media_id": None, "lat": 10., "lon": 8., "type": "start",
     "is_acknowledged": False, "created_at": "2020-11-03T11:18:45.447773"},
]

ACCESS_TABLE_FOR_DB = list(map(update_only_datetime, ACCESS_TABLE))
USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
EVENT_TABLE_FOR_DB = list(map(update_only_datetime, EVENT_TABLE))
ALERT_TABLE_FOR_DB = list(map(update_only_datetime, ALERT_TABLE))
MEDIA_TABLE_FOR_DB = list(map(update_only_datetime, MEDIA_TABLE))


async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE_FOR_DB)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    await populate_db(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await populate_db(test_db, db.events, EVENT_TABLE_FOR_DB)
    await populate_db(test_db, db.alerts, ALERT_TABLE_FOR_DB)
    await populate_db(test_db, db.media, MEDIA_TABLE_FOR_DB)


@pytest.mark.asyncio
async def test_get_alert(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/alerts/1")
    assert response.status_code == 200
    response_json = response.json()
    response_json["created_at"] = parse_time(response_json["created_at"])
    assert response_json == ALERT_TABLE_FOR_DB[0]


@pytest.mark.parametrize(
    "alert_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_alert_invalid(test_app_asyncio, test_db, monkeypatch, alert_id, status_code, status_details):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get(f"/alerts/{alert_id}")
    assert response.status_code == status_code, alert_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_alerts(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/alerts/")
    assert response.status_code == 200
    assert response.json() == ALERT_TABLE


@pytest.mark.asyncio
async def test_fetch_ongoing_alerts(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/alerts/ongoing")
    assert response.status_code == 200
    assert response.json() == [x for x in ALERT_TABLE if x["id"] == 3]


@pytest.mark.asyncio
async def test_fetch_unacknowledged_alerts(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/alerts/unacknowledged")
    assert response.status_code == 200
    assert response.json() == [x for x in ALERT_TABLE if x["is_acknowledged"] is False]


@pytest.mark.asyncio
async def test_create_alert(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    test_payload = {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "end"}
    test_response = {"id": len(ALERT_TABLE) + 1, **test_payload, "media_id": None, "is_acknowledged": False}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/alerts/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

    new_alert_in_db = await get_entry_in_db(test_db, db.alerts, json_response["id"])
    new_alert_in_db = dict(**new_alert_in_db)
    assert new_alert_in_db['created_at'] > utc_dt and new_alert_in_db['created_at'] < datetime.utcnow()


@pytest.mark.asyncio
async def test_create_alert_by_device(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    test_payload = {"event_id": 2, "lat": 10., "lon": 8., "type": "end"}
    # Device_id is 99 because it is the identified device
    test_response = {"id": len(ALERT_TABLE) + 1,
                     "device_id": 1, **test_payload,
                     "media_id": None, "is_acknowledged": False}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/alerts/from-device", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    new_alert_in_db = await get_entry_in_db(test_db, db.alerts, json_response["id"])
    new_alert_in_db = dict(**new_alert_in_db)
    assert new_alert_in_db['created_at'] > utc_dt and new_alert_in_db['created_at'] < datetime.utcnow()


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "restart"}, 422],
        [{"event_id": 2, "lat": 10., "lon": 8., "type": "end"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_create_alert_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.post("/alerts/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_alert(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    test_payload = {"device_id": 1, "event_id": 1, "lat": 10., "lon": 8., "type": "end"}
    response = await test_app_asyncio.put("/alerts/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    updated_alert_in_db = await get_entry_in_db(test_db, db.alerts, 1)
    updated_alert_in_db = dict(**updated_alert_in_db)
    for k, v in test_payload.items():
        assert v == updated_alert_in_db[k]


@pytest.mark.asyncio
async def test_acknowledge_alert(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put("/alerts/3/acknowledge")
    assert response.status_code == 200
    updated_alert_in_db = await get_entry_in_db(test_db, db.alerts, 3)
    updated_alert_in_db = dict(**updated_alert_in_db)
    assert updated_alert_in_db.is_acknowledged == True


@pytest.mark.parametrize(
    "alert_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"type": "start"}, 422],
        [999, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "start", "is_acknowledged": True}, 404],
        [1, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "restart", "is_acknowledged": True}, 422],
        [0, {"device_id": 2, "event_id": 2, "lat": 10., "lon": 8., "type": "start", "is_acknowledged": True}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_alert_invalid(test_app_asyncio, test_db, monkeypatch, alert_id, payload, status_code):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put(f"/alerts/{alert_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_delete_alert(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete("/alerts/1/")
    assert response.status_code == 200
    assert response.json() == ALERT_TABLE[0]
    remaining_alerts = await test_app_asyncio.get("/alerts/")
    for entry in remaining_alerts.json():
        assert entry['id'] != 1


@pytest.mark.asyncio
async def test_link_media_owner(test_app_asyncio, test_db, monkeypatch):
    # Create Alert (Identical code to the create_alert above)
    mock_alert_table = deepcopy(ALERT_TABLE)
    # Set device_id to 99 because it is the one that is authentified in our testConfig.
    mock_alert_table[0]["device_id"] = 99
    await init_test_db(monkeypatch, test_db)

    test_payload = {"media_id": 1}
    updated_alert = mock_alert_table[0]
    test_response = updated_alert.copy()
    test_response.update(test_payload)

    response = await test_app_asyncio.put(f"/alerts/{updated_alert['id']}/link-media", data=json.dumps(test_payload))
    assert response.status_code == 200
    updated_alert_in_db = await get_entry_in_db(test_db, db.alerts, 1)
    updated_alert_in_db = dict(**updated_alert_in_db)
    for k, v in test_payload.items():
        assert v == updated_alert_in_db[k]


@pytest.mark.asyncio
async def test_link_media_owner_not_allowed(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    test_payload = {"media_id": 1}
    alert_not_owned = 3
    response = await test_app_asyncio.put(f"/alerts/{alert_not_owned}/link-media", data=json.dumps(test_payload))
    assert response.status_code == 400


@pytest.mark.asyncio
async def test_link_non_existing_media(test_app_asyncio, test_db, monkeypatch):
    await init_test_db(monkeypatch, test_db)

    test_payload = {"media_id": 100}

    alert_owned = 1
    # Alert 1 because it is owned by the device 1
    response = await test_app_asyncio.put(f"/alerts/{alert_owned}/link-media", data=json.dumps(test_payload))
    assert response.status_code == 404


@pytest.mark.parametrize(
    "alert_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_alert_invalid(test_app_asyncio, test_db, monkeypatch, alert_id, status_code, status_details):
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete(f"/alerts/{alert_id}/")
    assert response.status_code == status_code, print(alert_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(alert_id)
