import pytest

from app.api import crud, security


MOCK_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "first_pwd_hashed", "scopes": "me"},
    {"id": 2, "login": "second_login", "hashed_password": "second_pwd_hashed", "scopes": "me"},
]


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
    local_db = MOCK_TABLE.copy()
    async def mock_fetch_one(table, query_filters):
        for entry in local_db:
            if all(entry[k] == v for k, v in query_filters):
                return entry
        return None

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    # Override cred verification
    async def verify_password(plain_password, hashed_password):
        return hashed_password == f"{plain_password}_hashed"

    monkeypatch.setattr(security, "verify_password", verify_password)

    response = test_app.post("/login/access-token", data=payload)

    assert response.status_code == status_code, print(payload)
    if isinstance(status_detail, str):
        assert response.json()['detail'] == status_detail
