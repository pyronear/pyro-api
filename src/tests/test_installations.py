import json
import pytest
from copy import deepcopy
from datetime import datetime

from app import db
from app.api import crud
from app.api.routes import installations
from tests.conf_test_db import get_entry_in_db, populate_db


MEDIA_TABLE = [
    {"id": 1, "device_id": 1, "type": "image", "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 1, "type": "video", "created_at": "2020-10-13T09:18:45.447773"},
]

ACCESS_TABLE = [{"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "me"},
                {"id": 2, "login": "first_device", "hashed_password": "hashed_pwd", "scopes": "device"},
                {"id": 3, "login": "second_device", "hashed_password": "hashed_pwd", "scopes": "device"}]

USER_TABLE = [{"id": 1, "login": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"}]


DEVICE_TABLE = [{
    "id": 1, "login": "first_device", "owner_id": 1, "access_id": 2, "specs": "v0.1", "elevation": None, "lat": None, 
    "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_device", "owner_id": 1, "access_id": 3, "specs": "v0.1", "elevation": None, "lat": None,
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


SITE_TABLE = [
    {"id": 1, "name": "my_first_tower", "lat": 44.1, "lon": -0.7, "type": "tower", "country": "FR", "geocode": "40",
     "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "name": "my_first_station", "lat": 44.1, "lon": 3.9, "type": "station", "country": "FR", "geocode": "30",
     "created_at": "2020-09-13T08:18:45.447773"},
]

INSTALLATION_TABLE = [
    {"id": 1, "device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.,
     "start_ts": None, "end_ts": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "device_id": 2, "site_id": 2, "elevation": 58., "lat": 5., "lon": 8., "yaw": 10., "pitch": 0.,
     "start_ts": None, "end_ts": None, "created_at": "2020-11-13T08:18:45.447773"},
]


DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"


def update_only_datetime(entity_as_dict):
    to_return = entity_as_dict.copy()
    if "created_at" in to_return:
        to_return["created_at"] = datetime.strptime(to_return["created_at"], DATETIME_FORMAT)
    return to_return


ACCESS_TABLE_FOR_DB = list(map(update_only_datetime, ACCESS_TABLE))
USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))
EVENT_TABLE_FOR_DB = list(map(update_only_datetime, EVENT_TABLE))
ALERT_TABLE_FOR_DB = list(map(update_only_datetime, ALERT_TABLE))
MEDIA_TABLE_FOR_DB = list(map(update_only_datetime, MEDIA_TABLE))
SITE_TABLE_FOR_DB = list(map(update_only_datetime, SITE_TABLE))
INSTALLATION_TABLE_FOR_DB = list(map(update_only_datetime, INSTALLATION_TABLE))


async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE_FOR_DB)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)

    await populate_db(test_db, db.devices, DEVICE_TABLE_FOR_DB)
    await populate_db(test_db, db.events, EVENT_TABLE_FOR_DB)
    await populate_db(test_db, db.alerts, ALERT_TABLE_FOR_DB)
    await populate_db(test_db, db.media, MEDIA_TABLE_FOR_DB)
    await populate_db(test_db, db.sites, SITE_TABLE_FOR_DB)
    await populate_db(test_db, db.installations, INSTALLATION_TABLE_FOR_DB)


@pytest.mark.asyncio
async def test_get_installation(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/installations/1")
    assert response.status_code == 200
    assert response.json() == INSTALLATION_TABLE[0]


@pytest.mark.parametrize(
    "installation_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_installation_invalid(test_app_asyncio, test_db, monkeypatch, installation_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get(f"/installations/{installation_id}")
    assert response.status_code == status_code, installation_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_installations(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/installations/")
    assert response.status_code == 200
    assert response.json() == INSTALLATION_TABLE


@pytest.mark.asyncio
async def test_create_installation(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}
    test_response = {"id": len(INSTALLATION_TABLE) + 1, **test_payload, "start_ts": None, "end_ts": None}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post("/installations/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response

    new_installation_in_db = await get_entry_in_db(test_db, db.installations, json_response["id"])
    new_installation_in_db = dict(**new_installation_in_db)

    # Timestamp consistency
    assert new_installation_in_db['created_at'] > utc_dt and new_installation_in_db['created_at'] < datetime.utcnow()

@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"device_id": 1, "site_id": 1, "elevation": "high", "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}, 422],
        [{"device_id": 1, "site_id": 1, "elevation": 100., "lat": 0., "lon": 0.}, 422],
    ],
)
@pytest.mark.asyncio
async def test_create_installation_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.post("/installations/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_installation(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}
    response = await test_app_asyncio.put("/installations/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    updated_installation_in_db = await get_entry_in_db(test_db, db.installations, 1)
    updated_installation_in_db = dict(**updated_installation_in_db)
    for k, v in updated_installation_in_db.items():
        assert v == test_payload.get(k, INSTALLATION_TABLE_FOR_DB[0][k])


@pytest.mark.parametrize(
    "installation_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"device_id": 1}, 422],
        [999, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}, 404],
        [1, {"device_id": 1, "site_id": 1, "elevation": "high", "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}, 422],
        [0, {"device_id": 1, "site_id": 1, "elevation": 123., "lat": 0., "lon": 0., "yaw": 0., "pitch": 0.}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_installation_invalid(test_app_asyncio, test_db, monkeypatch, installation_id, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put(f"/installations/{installation_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_delete_installation(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete("/installations/1/")
    assert response.status_code == 200
    assert response.json() == INSTALLATION_TABLE[0]
    remaining_installations = await test_app_asyncio.get("/installations/")
    for entry in remaining_installations.json():
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "installation_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_installation_invalid(test_app_asyncio, test_db, monkeypatch, installation_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete(f"/installations/{installation_id}/")
    assert response.status_code == status_code, print(installation_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(installation_id)
