import json
import pytest
from datetime import datetime

from app import db
from app.api import crud, security
from tests.conf_test_db import get_entry_in_db, populate_db
from tests.utils import update_only_datetime

USER_TABLE = [
    {"id": 1, "login": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "connected_user", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

DEVICE_TABLE = [
    {"id": 1, "login": "connected_device", "owner_id": 1,
     "access_id": 3, "specs": "raspberry", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_device", "owner_id": 2, "access_id": 4, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 3, "login": "third_device", "owner_id": 1, "access_id": 5, "specs": "v0.1", "elevation": None,
     "lat": None, "lon": None, "yaw": None, "pitch": None, "last_ping": None,
     "created_at": "2020-10-13T08:18:45.447773"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_user", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 2, "login": "connected_user", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 3, "login": "first_device", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 4, "login": "second_device", "hashed_password": "second_pwd_hashed", "scopes": "device"},
    {"id": 5, "login": "connected_device", "hashed_password": "third_pwd_hashed", "scopes": "device"},
]


ACCESS_TABLE_FOR_DB = list(map(update_only_datetime, ACCESS_TABLE))
USER_TABLE_FOR_DB = list(map(update_only_datetime, USER_TABLE))
DEVICE_TABLE_FOR_DB = list(map(update_only_datetime, DEVICE_TABLE))


async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    monkeypatch.setattr(crud, "database", test_db)
    await populate_db(test_db, db.accesses, ACCESS_TABLE_FOR_DB)
    await populate_db(test_db, db.users, USER_TABLE_FOR_DB)
    await populate_db(test_db, db.devices, DEVICE_TABLE_FOR_DB)


@pytest.mark.asyncio
async def test_get_device(test_app_asyncio, test_db, monkeypatch):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/devices/1")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in DEVICE_TABLE[0].items() if k != "access_id"}


@pytest.mark.parametrize(
    "device_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_device_invalid(test_app_asyncio, test_db, monkeypatch, device_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get(f"/devices/{device_id}")
    assert response.status_code == status_code, device_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


@pytest.mark.asyncio
async def test_fetch_devices(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.get("/devices/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in DEVICE_TABLE]

    # Self version
    response = await test_app_asyncio.get("/devices/my-devices")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"}
                               for entry in DEVICE_TABLE if entry['owner_id'] == 2]


@pytest.mark.parametrize(
    "payload, route",
    [
        [{"login": "third_device", "owner_id": 1, "specs": "v0.2", "password": "my_pwd"}, "/devices/"],  # existing device
        [{"login": "third_device", "specs": "v0.2", "password": "my_pwd"}, "/devices/register"],  # password too short
    ],
)
@pytest.mark.asyncio
async def test_create_device(test_app_asyncio, test_db, monkeypatch, payload, route):

    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_response = {"id": len(DEVICE_TABLE) + 1, "login": payload['login'],
                     "owner_id": payload.get('owner_id', 2), "specs": payload['specs']}

    utc_dt = datetime.utcnow()
    response = await test_app_asyncio.post(route, data=json.dumps(payload))

    assert response.status_code == 201, print(response.json()['detail'])
    # Response content
    json_response = response.json()
    for k, v in test_response.items():
        assert v == json_response[k]

    new_device_in_db = await get_entry_in_db(test_db, db.devices, json_response["id"])
    new_device_in_db = dict(**new_device_in_db)

    new_access_in_db = await get_entry_in_db(test_db, db.accesses, len(ACCESS_TABLE) + 1)
    new_access_in_db = dict(**new_access_in_db)

    # Timestamp consistency
    assert new_device_in_db['created_at'] > utc_dt and new_device_in_db['created_at'] < datetime.utcnow()
    # Access table updated
    assert new_access_in_db['hashed_password'] == f"{payload['password']}_hashed"


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"login": "first_device", "owner_id": 1, "specs": "v0.2", "password": "my_pwd"}, 400],  # existing device
        [{"login": "third_device", "owner_id": 1, "specs": "v0.2", "password": "pw"}, 422],  # password too short
        [{"login": "third_device", "specs": "v0.2", "password": "my_pwd"}, 422],  # missing owner
    ],
)
@pytest.mark.asyncio
async def test_create_device_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.post("/devices/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"login": "first_device", "specs": "v0.2", "password": "my_pwd"}, 400],  # existing device
        [{"login": "third_device", "specs": "v0.2", "password": "pw"}, 422],  # password too short
        [{"login": "third_device", "password": "my_pwd"}, 422],  # missing owner
    ],
)
@pytest.mark.asyncio
async def test_register_my_device_invalid(test_app_asyncio, test_db, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.post("/devices/register", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_device(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"login": "renamed_device", "owner_id": 1, "access_id": 3, "specs": "v0.1"}
    response = await test_app_asyncio.put("/devices/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    updated_device_in_db = await get_entry_in_db(test_db, db.devices, 1)
    updated_device_in_db = dict(**updated_device_in_db)
    for k, v in updated_device_in_db.items():
        assert v == test_payload.get(k, DEVICE_TABLE_FOR_DB[0][k])


@pytest.mark.parametrize(
    "device_id, payload, status_code",
    [
        [1, {}, 422],
        [999, {"login": "renamed_device", "owner_id": 1, "access_id": 1, "specs": "v0.1"}, 404],
        [1, {"login": 1, "owner_id": 1, "access_id": 1, "specs": "v0.1"}, 422],
        [1, {"login": "renamed_device"}, 422],
        [0, {"login": "renamed_device", "owner_id": 1, "access_id": 1, "specs": "v0.1"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_device_invalid(test_app_asyncio, test_db, monkeypatch, device_id, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put(f"/devices/{device_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_device_password(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"password": "new_password"}
    response = await test_app_asyncio.put("/devices/1/pwd", data=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in DEVICE_TABLE[0].items() if k != 'access_id'}
    new_access_in_db = await get_entry_in_db(test_db, db.accesses, DEVICE_TABLE[0]["access_id"])
    new_access_in_db = dict(**new_access_in_db)
    assert new_access_in_db['hashed_password'] == f"{test_payload['password']}_hashed"


@pytest.mark.parametrize(
    "device_id, payload, status_code",
    [
        [1, {}, 422],
        [999, {"password": "renamed_user"}, 404],
        [1, {"password": 1}, 422],
        [1, {"password": "me"}, 422],
        [0, {"password": "renamed_user"}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_device_password_invalid(test_app_asyncio, test_db, monkeypatch, device_id, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put(f"/devices/{device_id}/pwd", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


@pytest.mark.asyncio
async def test_update_device_location(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    test_payload = {"lon": 5.}
    response = await test_app_asyncio.put("/devices/2/location", data=json.dumps(test_payload))
    assert response.status_code == 200

    updated_device_in_db = await get_entry_in_db(test_db, db.devices, 2)
    updated_device_in_db = dict(**updated_device_in_db)
    for k, v in response.json().items():
        if k not in ['access_id', 'created_at']:
            assert v == updated_device_in_db[k]
    for k, v in test_payload.items():
        assert updated_device_in_db[k] == v

    # Self version
    response = await test_app_asyncio.put("/devices/my-location", data=json.dumps(test_payload))
    updated_device_in_db = await get_entry_in_db(test_db, db.devices, 1)
    updated_device_in_db = dict(**updated_device_in_db)
    assert response.status_code == 200
    for k, v in response.json().items():
        if k not in ['access_id', 'created_at']:
            assert v == updated_device_in_db[k]
    for k, v in test_payload.items():
        assert updated_device_in_db[k] == v


@pytest.mark.parametrize(
    "device_id, payload, status_code",
    [
        [999, {"lon": 5.}, 404],
        [1, {"lon": 5.}, 400],
        [2, {"lon": "position"}, 422],
        [0, {"lon": 5.}, 422],
    ],
)
@pytest.mark.asyncio
async def test_update_device_location_invalid(test_app_asyncio, test_db, monkeypatch, device_id, payload, status_code):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.put(f"/devices/{device_id}/location", data=json.dumps(payload))
    assert response.status_code == status_code, print(device_id, payload)


@pytest.mark.asyncio
async def test_heartbeat(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    utc_dt = datetime.utcnow()

    response = await test_app_asyncio.put("/devices/heartbeat")
    assert response.status_code == 200
    json_response = response.json()
    # Everything should be identical apart from ping
    assert datetime.utcnow() > datetime.fromisoformat(json_response['last_ping'])
    assert utc_dt < datetime.fromisoformat(json_response['last_ping'])

    updated_device_in_db = await get_entry_in_db(test_db, db.devices, 1)
    updated_device_in_db = dict(**updated_device_in_db)

    for k, v in updated_device_in_db.items():
        if k == 'last_ping':
            assert v != DEVICE_TABLE[0][k]
        elif k != 'created_at':
            assert v == DEVICE_TABLE[0][k]


@pytest.mark.asyncio
async def test_delete_device(test_app_asyncio, test_db, monkeypatch):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete("/devices/1/")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in DEVICE_TABLE[0].items() if k != 'access_id'}
    remaining_devices = await test_app_asyncio.get("/devices/")
    for entry in remaining_devices.json():
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "device_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_delete_device_invalid(test_app_asyncio, test_db, monkeypatch, device_id, status_code, status_details):
    # Sterilize DB interactions
    await init_test_db(monkeypatch, test_db)

    response = await test_app_asyncio.delete(f"/devices/{device_id}/")
    assert response.status_code == status_code, print(device_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(device_id)
