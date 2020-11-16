import json
import pytest

from app.api import crud
from app.api.deps import get_current_access, get_current_user
from app.api.schemas import AccessRead, UserRead


@pytest.mark.asyncio
async def testGetCurrentUser(test_app, monkeypatch): 

    test_user_data = [
        {"username": "JohnDoe", "id": 1, "access_id":1},
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