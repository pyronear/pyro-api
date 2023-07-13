import pytest
import pytest_asyncio

from app import db
from app.api import crud
from tests.db_utils import fill_table

GROUP_TABLE = [
    {"id": 1, "name": "first_group"},
]

ACCESS_TABLE = [
    {"id": 1, "login": "first_login", "hashed_password": "hashed_pwd", "scope": "user", "group_id": 1},
    {"id": 2, "login": "second_login", "hashed_password": "hashed_pwd", "scope": "admin", "group_id": 1},
    {"id": 3, "login": "third_login", "hashed_password": "hashed_pwd", "scope": "device", "group_id": 1},
]


@pytest_asyncio.fixture(scope="function")
async def init_test_db(monkeypatch, test_db):
    monkeypatch.setattr(crud.base, "database", test_db)
    await fill_table(test_db, db.groups, GROUP_TABLE)
    await fill_table(test_db, db.accesses, ACCESS_TABLE)


@pytest.mark.parametrize(
    "access_idx, access_id, status_code, status_details",
    [
        [None, 1, 401, "Not authenticated"],
        [0, 1, 403, "Your access scope is not compatible with this operation."],
        [0, 2, 403, "Your access scope is not compatible with this operation."],
        [0, 3, 403, "Your access scope is not compatible with this operation."],
        [2, 3, 403, "Your access scope is not compatible with this operation."],
        [1, 1, 200, None],
        [1, 2, 200, None],
        [1, 999, 404, "Table accesses has no entry with id=999"],
        [1, 0, 422, None],
    ],
)
@pytest.mark.asyncio
async def test_get_access(init_test_db, test_app_asyncio, access_idx, access_id, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get(f"/accesses/{access_id}", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details

    if response.status_code == 200:
        access = None
        for _access in ACCESS_TABLE:
            if _access["id"] == access_id:
                access = _access
                break
        assert response.json() == {k: v for k, v in access.items() if k != "hashed_password"}


@pytest.mark.parametrize(
    "access_idx, status_code, status_details",
    [
        [None, 401, "Not authenticated"],
        [0, 403, "Your access scope is not compatible with this operation."],
        [1, 200, None],
    ],
)
@pytest.mark.asyncio
async def test_fetch_accesses(init_test_db, test_app_asyncio, access_idx, status_code, status_details):
    # Create a custom access token
    auth = None
    if isinstance(access_idx, int):
        auth = await pytest.get_token(ACCESS_TABLE[access_idx]["id"], ACCESS_TABLE[access_idx]["scope"].split())

    response = await test_app_asyncio.get("/accesses/", headers=auth)
    assert response.status_code == status_code

    if isinstance(status_details, str):
        assert response.json()["detail"] == status_details
    if response.status_code == 200:
        assert response.json() == [{k: v for k, v in entry.items() if k != "hashed_password"} for entry in ACCESS_TABLE]
