import json
import pytest
from copy import deepcopy

from app.api import crud
from app.api.routes import accesses


ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scopes": "me"},
]


def _patch_session(monkeypatch, mock_table):
    # DB patching
    monkeypatch.setattr(accesses, "accesses", mock_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(crud, "get", pytest.mock_get)
    monkeypatch.setattr(crud, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(crud, "fetch_one", pytest.mock_fetch_one)
    monkeypatch.setattr(crud, "post", pytest.mock_post)
    monkeypatch.setattr(crud, "put", pytest.mock_put)
    monkeypatch.setattr(crud, "delete", pytest.mock_delete)


def test_get_access(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    response = test_app.get("/accesses/1")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in mock_access_table[0].items() if k != "hashed_password"}


@pytest.mark.parametrize(
    "access_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_get_access_invalid(test_app, monkeypatch, access_id, status_code, status_details):
    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    response = test_app.get(f"/accesses/{access_id}")
    assert response.status_code == status_code, access_id
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details


def test_fetch_accesses(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    response = test_app.get("/accesses/")
    assert response.status_code == 200
    assert response.json() == [{k: v for k, v in entry.items() if k != "hashed_password"}
                               for entry in mock_access_table]


def test_create_access(test_app, monkeypatch):

    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    test_payload = {"login": "third_login", "scopes": "me", "password": "PickARobustOne"}
    test_response = {"id": len(mock_access_table) + 1, **test_payload}

    response = test_app.post("/accesses/", data=json.dumps(test_payload))

    assert response.status_code == 201
    assert response.json() == {k: v for k, v in test_response.items() if k != "password"}


@pytest.mark.parametrize(
    "payload, status_code, status_details",
    [
        [{"login": "first_login", "password": "PickARobustOne", "scopes": "me"}, 400,
         "An entry with login='first_login' already exists."],
        [{"login": "third_login", "scopes": "me", "hashed_password": "PickARobustOne"}, 422, None],
        [{"login": 1, "scopes": "me", "password": "PickARobustOne"}, 422, None],
        [{"login": "third_login", "scopes": "me"}, 422, None],
    ],
)
def test_create_access_invalid(test_app, monkeypatch, payload, status_code, status_details):
    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    response = test_app.post("/accesses/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(payload)


def test_update_access(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    test_payload = {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}
    response = test_app.put("/accesses/1/", data=json.dumps(test_payload))
    assert response.status_code == 200
    for k, v in mock_access_table[0].items():
        assert v == test_payload.get(k, ACCESS_TABLE[0][k])


@pytest.mark.parametrize(
    "access_id, payload, status_code",
    [
        [1, {}, 422],
        [1, {"login": "first_login"}, 422],
        [999, {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}, 404],
        [1, {"login": 1, "scopes": "me", "password": "PickAnotherRobustOne"}, 422],
        [0, {"login": "first_login", "scopes": "me", "password": "PickAnotherRobustOne"}, 422],
    ],
)
def test_update_access_invalid(test_app, monkeypatch, access_id, payload, status_code):
    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    response = test_app.put(f"/accesses/{access_id}/", data=json.dumps(payload))
    assert response.status_code == status_code, print(payload)


def test_delete_access(test_app, monkeypatch):
    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    response = test_app.delete("/accesses/1/")
    assert response.status_code == 200
    assert response.json() == {k: v for k, v in ACCESS_TABLE[0].items() if k != "hashed_password"}
    for entry in mock_access_table:
        assert entry['id'] != 1


@pytest.mark.parametrize(
    "access_id, status_code, status_details",
    [
        [999, 404, "Entry not found"],
        [0, 422, None],
    ],
)
def test_delete_access_invalid(test_app, monkeypatch, access_id, status_code, status_details):
    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    response = test_app.delete(f"/accesses/{access_id}/")
    assert response.status_code == status_code, print(payload)
    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details, print(payload)
