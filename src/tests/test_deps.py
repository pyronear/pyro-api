import pytest

from app.api import crud
from app.api.deps import get_current_user, get_current_device
from app.api.schemas import AccessRead, UserRead, DeviceOut


@pytest.mark.asyncio
async def testGetCurrentUser(test_app, monkeypatch):

    test_user_data = [
        {"username": "JohnDoe", "id": 1, "access_id": 1},
    ]

    async def mock_fetch_one(table, query_filters):
        for entry in test_user_data:
            for queryFilterKey, queryFilterValue in query_filters.items():
                valid_entry = True
                if entry[queryFilterKey] != queryFilterValue:
                    valid_entry = False
            if valid_entry:
                return entry

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    response = await get_current_user(AccessRead(id=1, login="JohnDoe", scopes="me"))
    assert response == UserRead(**test_user_data[0])


@pytest.mark.asyncio
async def testGetCurrentDevice(test_app, monkeypatch):

    MIN_PAYLOAD = {"name": "my_device", "owner_id": 1, "specs": "my_specs", "password": "my_password"}
    FULL_PAYLOAD = {
        **MIN_PAYLOAD,
        "lat": None,
        "lon": None,
        "elevation": None,
        "yaw": None,
        "pitch": None,
        "last_ping": None,
    }
    test_device_data = [
        {"id": 1, **FULL_PAYLOAD, "access_id": 1}
    ]

    async def mock_fetch_one(table, query_filters):
        for entry in test_device_data:
            for queryFilterKey, queryFilterValue in query_filters.items():
                valid_entry = True
                if entry[queryFilterKey] != queryFilterValue:
                    valid_entry = False
            if valid_entry:
                return entry

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    response = await get_current_device(AccessRead(id=1, login="JohnDoe", scopes="me"))
    assert response == DeviceOut(**test_device_data[0])
