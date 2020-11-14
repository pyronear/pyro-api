import pytest
from starlette.testclient import TestClient
from datetime import datetime

from app.main import app
from app.api.schemas import UserRead, DeviceOut
from app.api.deps import get_current_user, get_current_device


async def mock_current_user():
    return UserRead(id=99, username="connected_user", created_at=datetime.now())


async def mock_current_device():
    return DeviceOut(id=99, owner_id=1, specs="raspberry", name="connected_device", created_at=datetime.now())


# Sterilize all DB interactions
async def mock_get(entry_id, table):
    for entry in table:
        if entry['id'] == entry_id:
            return entry
    return None


async def mock_fetch_all(table, query_filters):
    if query_filters is None:
        return table
    response = []
    for entry in table:
        if all(entry[k] == v for k, v in query_filters):
            response.append(entry)
    return response


async def mock_fetch_one(table, query_filters):
    for entry in table:
        if all(entry[k] == v for k, v in query_filters):
            return entry
    return None


async def mock_post(payload, table):
    payload_dict = payload.dict()
    payload_dict['created_at'] = datetime.utcnow()
    payload_dict['id'] = len(table) + 1
    table.append(payload_dict)
    return payload_dict['id']


async def mock_put(entry_id, payload, table):
    for idx, entry in enumerate(table):
        if entry['id'] == entry_id:
            for k, v in payload.dict().items():
                table[idx][k] = v
    return entry_id


async def mock_delete(entry_id, table):
    for idx, entry in enumerate(table):
        if entry['id'] == entry_id:
            del table[idx]
            break
    return entry_id


async def mock_hash_password(password):
    return f"{password}_hashed"


async def mock_verify_password(plain_password, hashed_password):
    return hashed_password == f"{plain_password}_hashed"


def pytest_configure():
    # CRUD patching
    pytest.mock_get = mock_get
    pytest.mock_fetch_all = mock_fetch_all
    pytest.mock_fetch_one = mock_fetch_one
    pytest.mock_post = mock_post
    pytest.mock_put = mock_put
    pytest.mock_delete = mock_delete
    pytest.mock_hash_password = mock_hash_password
    pytest.mock_verify_password = mock_verify_password


@pytest.fixture(scope="module")
def test_app():

    # Access-related patching
    app.dependency_overrides[get_current_user] = mock_current_user
    app.dependency_overrides[get_current_device] = mock_current_device

    client = TestClient(app)
    yield client  # testing happens here

    app.dependency_overrides = {}
