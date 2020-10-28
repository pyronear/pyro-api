import pytest

from app.api import crud
from app import security


@pytest.mark.parametrize(
    "payload, status_code",
    [
        [{"username": "foo"}, 422],
        [{"password": "foo"}, 422],
        [{"username": "unknown", "password": "foo"}, 400],  # unknown username
        [{"username": "first", "password": "first"}, 200],  # valid
        [{"username": "first", "password": "second"}, 400],  # wrong pwd
    ],
)
def test_access_token(test_app, monkeypatch, existing_users, payload, status_code):
    async def get_by_username(username: str):
        for u in existing_users:
            if u.username == username:
                return u

    async def verify_password(plain_password, hashed_password):
        return hashed_password == f"{plain_password}_hashed"

    monkeypatch.setattr(crud.user, "get_by_username", get_by_username)
    monkeypatch.setattr(security, "verify_password", verify_password)

    response = test_app.post("/login/access-token", data=payload)
    assert response.status_code == status_code, (payload, status_code,)
