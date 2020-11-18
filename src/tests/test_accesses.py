import json
import pytest
from copy import deepcopy

from app.api.crud import base
from app.api.routes import accesses


ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scopes": "me"},
]


def _patch_session(monkeypatch, mock_table):
    # DB patching
    monkeypatch.setattr(accesses, "accesses", mock_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(base, "get", pytest.mock_get)
    monkeypatch.setattr(base, "fetch_all", pytest.mock_fetch_all)
    monkeypatch.setattr(base, "fetch_one", pytest.mock_fetch_one)
    monkeypatch.setattr(base, "post", pytest.mock_post)
    monkeypatch.setattr(base, "put", pytest.mock_put)
    monkeypatch.setattr(base, "delete", pytest.mock_delete)


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