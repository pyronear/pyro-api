import pytest
from copy import deepcopy

from app.api import crud, security
from app.api.routes import login


ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "first_pwd_hashed", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "second_pwd_hashed", "scopes": "me"},
]


def _patch_session(monkeypatch, mock_table):
    # DB patching
    monkeypatch.setattr(login, "accesses", mock_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(crud, "fetch_one", pytest.mock_fetch_one)
    # Password
    monkeypatch.setattr(security, "verify_password", pytest.mock_verify_password)


@pytest.mark.parametrize(
    "payload, status_code, status_detail",
    [
        [{"username": "foo"}, 422, None],
        [{"password": "foo"}, 422, None],
        [{"username": "unknown", "password": "foo"}, 400, "Invalid credentials"],  # unknown username
        [{"username": "first", "password": "second"}, 400, "Invalid credentials"],  # wrong pwd
        [{"username": "first_login", "password": "first_pwd"}, 200, None],  # valid
    ],
)
def test_create_access_token(test_app, monkeypatch, payload, status_code, status_detail):

    # Sterilize DB interactions
    mock_access_table = deepcopy(ACCESS_TABLE)
    _patch_session(monkeypatch, mock_access_table)

    response = test_app.post("/login/access-token", data=payload)

    assert response.status_code == status_code, print(payload)
    if isinstance(status_detail, str):
        assert response.json()['detail'] == status_detail
