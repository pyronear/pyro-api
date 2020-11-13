import json
import pytest
from datetime import datetime

from app.api import crud

MIN_PAYLOAD = {"name": "my_site", "lat": 0., "lon": 0.}
FULL_PAYLOAD = {**MIN_PAYLOAD, "type": "tower"}


MOCK_DB = [
    {"id": 1, "name": "my_first_site", "lat": 0., "lon": 0., "type": "tower", "created_at": "2020-10-13T08:18:45.447773"},
]

def test_create_site(test_app, monkeypatch):

    local_db = MOCK_DB.copy()
    async def mock_post(payload, table):
        payload_dict = payload.dict()
        payload_dict['created_at'] = datetime.utcnow()
        payload_dict['id'] = len(local_db) + 1
        local_db.append(payload_dict)
        return payload_dict['id']

    monkeypatch.setattr(crud, "post", mock_post)


    test_payload = FULL_PAYLOAD
    test_response = {"id": len(local_db) + 1, **FULL_PAYLOAD}

    utc_dt = datetime.utcnow()
    response = test_app.post("/sites/", data=json.dumps(test_payload))

    assert response.status_code == 201
    json_response = response.json()
    assert {k: v for k, v in json_response.items() if k != 'created_at'} == test_response
    assert local_db[-1]['created_at'] > utc_dt


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"names": "my_site", "lat": 0., "lon": 0., "type": "tower"}, 422],
        [{"name": "my_site", "lat": 0.}, 422],
    ],
)
def test_create_site_invalid_json(test_app, payload, status_code):
    response = test_app.post("/sites/", data=json.dumps(payload))
    assert response.status_code == status_code


def test_get_site(test_app, monkeypatch):

    local_db = MOCK_DB.copy()
    async def mock_get(entry_id, table):
        for entry in local_db:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/sites/1")
    assert response.status_code == 200
    assert response.json() == local_db[0]


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_site_incorrect_id(test_app, monkeypatch, site_id, status_code, status_details):
    local_db = MOCK_DB.copy()
    async def mock_get(entry_id, table):
        for entry in local_db:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get(f"/sites/{site_id}")
    assert response.status_code == status_code, site_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_sites(test_app, monkeypatch):
    local_db = MOCK_DB.copy()
    async def mock_fetch_all(table, query_filter=None):
        return local_db

    monkeypatch.setattr(crud, "fetch_all", mock_fetch_all)

    response = test_app.get("/sites/")
    assert response.status_code == 200
    assert response.json() == local_db


def test_update_site(test_app, monkeypatch):
    local_db = MOCK_DB.copy()
    async def mock_get(entry_id, table):
        for entry in local_db:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        for idx, entry in enumerate(local_db):
            if entry['id'] == entry_id:
                for k, v in payload.dict().items():
                    local_db[idx][k] = v
        return entry_id

    monkeypatch.setattr(crud, "put", mock_put)

    test_payload = {"name": "renamed_site", "lat": 0., "lon": 0., "type": "tower"}
    response = test_app.put("/sites/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in local_db[0].items():
        assert v == test_payload.get(k, MOCK_DB[0][k])


@pytest.mark.parametrize(
    "site_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"site_name": "foo"}, 422],
        [999, {"name": "foo", "lat": 0., "lon": 0., "type": "tower"}, 404],
        [1, {"name": "1", "lat": 0., "lon": 0., "type": "tower"}, 422],
        [0, {"name": "foo", "lat": 0., "lon": 0., "type": "tower"}, 422],
    ],
)
def test_update_site_invalid(test_app, monkeypatch, site_id, payload, status_code):
    local_db = MOCK_DB.copy()
    async def mock_get(entry_id, table):
        for entry in local_db:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        for idx, entry in enumerate(local_db):
            if entry['id'] == entry_id:
                for k, v in payload.dict().items():
                    local_db[idx][k] = v
        return entry_id

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put(f"/sites/{site_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_remove_site(test_app, monkeypatch):
    local_db = MOCK_DB.copy()
    async def mock_get(entry_id, table):
        for entry in local_db:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(entry_id, table):
        for idx, entry in enumerate(local_db):
            if entry['id'] == entry_id:
                del local_db[idx]
                break
        return entry_id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/sites/1/")
    assert response.status_code == 200
    assert response.json() == MOCK_DB[0]
    for entry in local_db:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_remove_site_incorrect_id(test_app, monkeypatch, site_id, status_code, status_details):
    local_db = MOCK_DB.copy()
    async def mock_get(entry_id, table):
        for entry in local_db:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete(f"/sites/{site_id}/")
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details
