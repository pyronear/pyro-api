import pytest

from app.api import crud, deps
from app.api.schemas import AccessRead, UserRead, DeviceOut
from copy import deepcopy

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


def _patch_session(monkeypatch, mock_user_table=None, mock_device_table=None):
    # DB patching
    if mock_user_table is not None:
        monkeypatch.setattr(deps, "users", mock_user_table)
    if mock_device_table is not None:
        monkeypatch.setattr(deps, "devices", mock_device_table)
    # Sterilize all DB interactions through CRUD override
    monkeypatch.setattr(crud, "fetch_one", pytest.mock_fetch_one)


@pytest.mark.asyncio
async def test_get_current_user(test_app, monkeypatch):

    mock_user_table = deepcopy(USER_TABLE)
    _patch_session(monkeypatch, mock_user_table, None)

    response = await deps.get_current_user(AccessRead(id=1, login="JohnDoe", scopes="me"))
    assert response == UserRead(**mock_user_table[0])


@pytest.mark.asyncio
async def test_get_current_device(test_app, monkeypatch):

    mock_device_table = deepcopy(DEVICE_TABLE)
    _patch_session(monkeypatch, None, mock_device_table)

    response = await deps.get_current_device(AccessRead(id=1, login="JohnDoe", scopes="me"))
    assert response == DeviceOut(**mock_device_table[0])
