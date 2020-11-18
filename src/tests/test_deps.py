import pytest

from app.api import crud
from app.api.deps import get_current_user, get_current_device
from app.api.schemas import AccessRead, UserRead, DeviceOut

USER_TABLE = [
    {"id": 1, "login": "first_user", "access_id": 1, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 99, "login": "connected_user", "access_id": 2, "created_at": "2020-11-13T08:18:45.447773"},
]

DEVICE_TABLE = [
    {"id": 1, "login": "first_device", "owner_id": 1, "access_id": 1, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 2, "login": "second_device", "owner_id": 99, "access_id": 2, "specs": "v0.1", "elevation": None, "lat": None,
     "lon": None, "yaw": None, "pitch": None, "last_ping": None, "created_at": "2020-10-13T08:18:45.447773"},
    {"id": 99, "login": "connected_device", "owner_id": 1, "access_id": 3, "specs": "raspberry", "elevation": None,
     "lat": None, "lon": None, "yaw": None, "pitch": None, "last_ping": None,
     "created_at": "2020-10-13T08:18:45.447773"},
]


@pytest.mark.asyncio
async def testGetCurrentUser(test_app, monkeypatch):

    async def mock_fetch_one(table, query_filters):
        for entry in USER_TABLE:
            for query_filter_key, query_filter_value in query_filters.items():
                valid_entry = True
                if entry[query_filter_key] != query_filter_value:
                    valid_entry = False
            if valid_entry:
                return entry

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    response = await get_current_user(AccessRead(id=1, login="JohnDoe", scopes="me"))
    assert response == UserRead(**USER_TABLE[0])


@pytest.mark.asyncio
async def testGetCurrentDevice(test_app, monkeypatch):

    async def mock_fetch_one(table, query_filters):
        for entry in DEVICE_TABLE:
            for query_filter_key, query_filter_value in query_filters.items():
                valid_entry = True
                if entry[query_filter_key] != query_filter_value:
                    valid_entry = False
            if valid_entry:
                return entry

    monkeypatch.setattr(crud, "fetch_one", mock_fetch_one)

    response = await get_current_device(AccessRead(id=1, login="JohnDoe", scopes="me"))
    assert response == DeviceOut(**DEVICE_TABLE[0])
