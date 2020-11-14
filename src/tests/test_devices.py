import json
import pytest
from copy import deepcopy
from datetime import datetime
from fastapi import HTTPException

from app.api import crud, security
from app.api.routes import devices
from app.api.schemas import AccessRead, AccessCreation


DEVICE_TABLE = [
    {"id": 1, "name": "first_device", "owner_id": 1, "access_id": 1, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "name": "second_device", "owner_id": 99, "access_id": 2, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 99, "name": "connected_device", "owner_id": 1, "access_id": 3, "specs": "raspberry", "elevation": None,
     "lat": None, "lon": None, "yaw": None, "pitch": None, "last_ping": None,
     "created_at": "2020-10-13T08:18:45.447773"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_device", "hashed_password": "first_pwd_hashed", "scopes": "device"},
    {"id": 2, "login": "second_device", "hashed_password": "second_pwd_hashed", "scopes": "device"},
    {"id": 3, "login": "connected_device", "hashed_password": "third_pwd_hashed", "scopes": "device"},
]


def _patch_session(monkeypatch, mock_device_table, mock_access_table=None):
    # DB patching
    monkeypatch.setattr(devices, "devices", mock_device_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(crud, "get", pytest.mock_get)
    monkeypatch.setattr(crud, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(crud, "fetch_one", pytest.mock_fetch_one)
    monkeypatch.setattr(crud, "post", pytest.mock_post)
    monkeypatch.setattr(crud, "put", pytest.mock_put)
    monkeypatch.setattr(crud, "delete", pytest.mock_delete)
    # Password
    monkeypatch.setattr(security, "hash_password", pytest.mock_hash_password)
    # Access table specific
    if mock_access_table is not None:
        async def mock_update_pwd(payload, entry_id):
            for idx, entry in enumerate(mock_access_table):
                if entry["id"] == entry_id:
                    mock_access_table[idx]["hashed_password"] = await security.hash_password(payload.password)
                    return {"login": entry["login"]}

        monkeypatch.setattr(devices, "update_access_pwd", mock_update_pwd)

        async def mock_post_access(login, password, scopes):
            if any(entry['login'] == login for entry in mock_access_table):
                raise HTTPException(status_code=400, detail=f"An entry with login='{login}' already exists.")

            pwd = await pytest.mock_hash_password(password)
            access = AccessCreation(login=login, hashed_password=pwd, scopes=scopes)
            # Post on access table
            payload_dict = access.dict()
            payload_dict['id'] = len(mock_access_table) + 1
            mock_access_table.append(payload_dict)
            return AccessRead(id=payload_dict['id'], **access.dict())

        monkeypatch.setattr(devices, "post_access", mock_post_access)


def test_get_device(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, mock_device_table)

    response = test_app.get("/devices/1")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in mock_device_table[0].items() if k != "access_id"}


@pytest.mark.parametrize(
    "device_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_device_invalid(test_app, monkeypatch, device_id, status_code, status_details):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, mock_device_table)

    response = test_app.get(f"/devices/{device_id}")
    assert response.status_code == status_code, device_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_devices(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, mock_device_table)

    response = test_app.get("/devices/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"} for entry in mock_device_table]

    # Self version
    response = test_app.get("/devices/my-devices")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "access_id"}
                               for entry in mock_device_table if entry['owner_id'] == 99]


def test_create_device(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_device_table, mock_access_table)

    test_payload = {"name": "third_device", "owner_id": 1, "specs": "v0.2", "password": "my_pwd"}
    test_response = {"id": len(mock_device_table) + 1, "name": "third_device", "owner_id": 1, "specs": "v0.2"}

    utc_dt = datetime.utcnow()
    response = test_app.post("/devices/", data=json.dumps(test_payload))

    assert response.status_code == 201, print(response.json()['detail'])
    # Response content
    json_response = response.json()
    for k, v in test_response.items():
        assert v == json_response[k]
    # Timestamp consistency
    assert mock_device_table[-1]['created_at'] > utc_dt and mock_device_table[-1]['created_at'] < datetime.utcnow()
    # Access table updated
    assert mock_access_table[-1]['hashed_password'] == f"{test_payload['password']}_hashed"


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"name": "first_device", "owner_id": 1, "specs": "v0.2", "password": "my_pwd"}, 400],  # existing device
        [{"name": "third_device", "owner_id": 1, "specs": "v0.2", "password": "pw"}, 422],  # password too short
        [{"name": "third_device", "specs": "v0.2", "password": "my_pwd"}, 422],  # missing owner
    ],
)
def test_create_device_invalid(test_app, monkeypatch, payload, status_code):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_device_table, mock_access_table)

    response = test_app.post("/devices/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_device(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, mock_device_table)

    test_payload = {"name": "renamed_device", "owner_id": 1, "access_id": 1, "specs": "v0.1"}
    response = test_app.put("/devices/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in mock_device_table[0].items():
        assert v == test_payload.get(k, DEVICE_TABLE[0][k])


@pytest.mark.parametrize(
    "device_id, payload, status_code",
    [
        [1, {}, 422],
        [999, {"name": "renamed_device", "owner_id": 1, "access_id": 1, "specs": "v0.1"}, 404],
        [1, {"name": 1, "owner_id": 1, "access_id": 1, "specs": "v0.1"}, 422],
        [1, {"name": "renamed_device"}, 422],
        [0, {"name": "renamed_device", "owner_id": 1, "access_id": 1, "specs": "v0.1"}, 422],
    ],
)
def test_update_device_invalid(test_app, monkeypatch, device_id, payload, status_code):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, mock_device_table)

    response = test_app.put(f"/devices/{device_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_device_password(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_device_table, mock_access_table)

    test_payload = {"password": "new_password"}
    response = test_app.put("/devices/1/pwd", data=json.dumps(test_payload))
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in mock_device_table[0].items() if k != 'access_id'}
    assert mock_access_table[0]['hashed_password'] == f"{test_payload['password']}_hashed"


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
def test_update_device_password_invalid(test_app, monkeypatch, device_id, payload, status_code):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_device_table, mock_access_table)

    response = test_app.put(f"/devices/{device_id}/pwd", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_update_device_location(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_device_table, mock_access_table)

    test_payload = {"lon": 5.}
    response = test_app.put("/devices/2/location", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in response.json().items():
        if k not in ['access_id', 'created_at']:
            assert v == mock_device_table[1][k]
    for k, v in test_payload.items():
        assert mock_device_table[1][k] == v


@pytest.mark.parametrize(
    "device_id, payload, status_code",
    [
        [999, {"lon": 5.}, 400],
        [1, {"lon": 5.}, 400],
        [2, {"lon": "position"}, 422],
        [0, {"lon": 5.}, 422],
    ],
)
def test_update_device_location_invalid(test_app, monkeypatch, device_id, payload, status_code):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_device_table, mock_access_table)

    response = test_app.put(f"/devices/{device_id}/location", data=json.dumps(payload))
    assert response.status_code == status_code, print(device_id, payload)


def test_heartbeat(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, mock_device_table)

    utc_dt = datetime.utcnow()

    response = test_app.put("/devices/heartbeat")
    assert response.status_code == 200
    json_response = response.json()
    # Everything should be identical apart from ping
    assert datetime.utcnow() > datetime.fromisoformat(json_response['last_ping'])
    assert utc_dt < datetime.fromisoformat(json_response['last_ping'])

    for k, v in mock_device_table[2].items():
        if k == 'last_ping':
            assert v != DEVICE_TABLE[2][k]
        elif k != 'created_at':
            assert v == DEVICE_TABLE[2][k]


def test_delete_device(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, mock_device_table)

    response = test_app.delete("/devices/1/")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in DEVICE_TABLE[0].items() if k != 'access_id'}
    for entry in mock_device_table:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "device_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_device_invalid(test_app, monkeypatch, device_id, status_code, status_details):
    # Sterilize DB interactions
    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, mock_device_table)

    response = test_app.delete(f"/devices/{device_id}/")
    assert response.status_code == status_code, print(device_id)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(device_id)
