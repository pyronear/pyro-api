import json
import pytest

from app.api import crud

MIN_PAYLOAD = {"device_id": 1}
FULL_PAYLOAD = {**MIN_PAYLOAD, "type": "image"}


def test_create_media(test_app, monkeypatch):
    test_request_payload = FULL_PAYLOAD
    test_response_payload = {"id": 1, **FULL_PAYLOAD}

    async def mock_post(payload, table):
        return 1

    monkeypatch.setattr(crud, "post", mock_post)

    response = test_app.post("/media/", data=json.dumps(test_request_payload),)

    assert response.status_code == 201
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_response_payload


def test_create_media_invalid_json(test_app):
    response = test_app.post("/media/", data=json.dumps({"device": 1}))
    assert response.status_code == 422

    response = test_app.post("/media/", data=json.dumps({"device_id": 1, "type": "2"}))
    assert response.status_code == 422


def test_get_media(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/media/1")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_get_media_incorrect_id(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.get("/media/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.get("/media/0")
    assert response.status_code == 422


def test_fetch_medias(test_app, monkeypatch):
    test_data = [
        {"id": 1, **FULL_PAYLOAD},
        {"id": 2, **FULL_PAYLOAD},
    ]

    async def mock_get_all(table, query_filter=None):
        return test_data

    monkeypatch.setattr(crud, "fetch_all", mock_get_all)

    response = test_app.get("/media/")
    assert response.status_code == 200
    assert [{k: v for k, v in r.items() if k != 'created_at'} for r in response.json()] == test_data


def test_update_media(test_app, monkeypatch):
    test_update_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(entry_id, table):
        return True

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_put(entry_id, payload, table):
        return 1

    monkeypatch.setattr(crud, "put", mock_put)

    response = test_app.put("/media/1/", data=json.dumps(test_update_data))
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_update_data


@pytest.mark.parametrize(
    "media_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"type": "tower"}, 422],
        [999, FULL_PAYLOAD, 404],
        [1, {"device_id": "1", "type": "tower"}, 422],
        [0, FULL_PAYLOAD, 422],
    ],
)
def test_update_media_invalid(test_app, monkeypatch, media_id, payload, status_code):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.put(f"/media/{media_id}/", data=json.dumps(payload),)
    assert response.status_code == status_code, print(payload)


def test_remove_media(test_app, monkeypatch):
    test_data = {"id": 1, **FULL_PAYLOAD}

    async def mock_get(entry_id, table):
        return test_data

    monkeypatch.setattr(crud, "get", mock_get)

    async def mock_delete(entry_id, table):
        return entry_id

    monkeypatch.setattr(crud, "delete", mock_delete)

    response = test_app.delete("/media/1/")
    assert response.status_code == 200
    assert {k: v for k, v in response.json().items() if k != 'created_at'} == test_data


def test_remove_media_incorrect_id(test_app, monkeypatch):
    async def mock_get(entry_id, table):
        return None

    monkeypatch.setattr(crud, "get", mock_get)

    response = test_app.delete("/media/999/")
    assert response.status_code == 404
    assert response.json()["detail"] == "Entry not found"

    response = test_app.delete("/media/0/")
    assert response.status_code == 422
