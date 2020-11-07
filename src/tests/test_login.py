import pytest

from app.api import crud, security


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
def test_access_token(test_app, monkeypatch, payload, status_code):

    test_data = [
        {"login": "first", "hashed_password": "first_hashed", "scopes": "me", "id": 1},
        {"login": "second", "hashed_password": "second_hashed", "scopes": "me", "id": 2},
        {"login": "third", "hashed_password": "third_hashed", "scopes": "me admin", "id": 3},
        {"login": "fourth", "hashed_password": "fourth_hashed", "scopes": "device", "id": 4},
    ]

    async def mock_fetch_one(table, query_filters):
        for entry in test_data:
            for query_filter in query_filters:
                valid_entry = True
                if entry[query_filter[0]] != query_filter[1]:
                    valid_entry = False
            if valid_entry:
                return entry

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    async def verify_password(plain_password, hashed_password):
        return hashed_password == f"{plain_password}_hashed"

    monkeypatch.setattr(security, "verify_password", verify_password)

    response = test_app.post("/login/access-token", data=payload)
    assert response.status_code == status_code, (payload, status_code,)
