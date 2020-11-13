import json
import pytest

from app.api import crud

MIN_PAYLOAD = {"name": "my_site", "lat": 0., "lon": 0.}
FULL_PAYLOAD = {**MIN_PAYLOAD, "type": "tower"}


def test_create_site(test_app, monkeypatch):
    test_request_payload = FULL_PAYLOAD
    test_response_payload = {"id": 1, **FULL_PAYLOAD}

    # Sterilize DB interactions
    async def mock_post(payload, table):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/sites/", data=json.dumps(test_request_payload))

    assert response.status_code == 201
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_response_payload


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
    test_table = [{"id": 1, **FULL_PAYLOAD}]

    async def mock_get(entry_id, table):
        for entry in test_table:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/sites/1")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_table[0]


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_site_incorrect_id(test_app, monkeypatch, site_id, status_code, status_details):
    test_table = [{"id": 1, **FULL_PAYLOAD}]
    async def mock_get(entry_id, table):
        for entry in test_table:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get(f"/sites/{site_id}")
    assert response.status_code == status_code, site_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_sites(test_app, monkeypatch):
    test_table = [
        {"id": 1, **FULL_PAYLOAD},
        {"id": 2, **FULL_PAYLOAD},
    ]

    async def mock_fetch_all(table, query_filter=None):
        return test_table

    monkeypatch.setattr(crud, "fetch_all", mock_fetch_all)

    response = test_app.get("/sites/")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != 'created_at'} for r in response.json()] == test_table


def test_update_site(test_app, monkeypatch):
    test_table = [{"id": 1, **FULL_PAYLOAD}]

    async def mock_get(entry_id, table):
        for entry in test_table:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        return entry_id

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/sites/1/", data=json.dumps(test_table[0]))
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_table[0]


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
    test_table = [{"id": 1, **FULL_PAYLOAD}]
    async def mock_get(entry_id, table):
        for entry in test_table:
            if entry['id'] == entry_id:
                return entry
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        return entry_id

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put(f"/sites/{site_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_remove_site(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(entry_id, table):
        return entry_id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/sites/1/")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


@pytest.mark.parametrize(
    "site_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_remove_site_incorrect_id(test_app, monkeypatch, site_id, status_code, status_details):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete(f"/sites/{site_id}/")
    assert response.status_code == status_code
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details
