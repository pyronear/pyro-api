import asyncio
from datetime import datetime
from typing import AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
import requests
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints import login, users
from app.core.config import settings
from app.core.security import create_access_token
from app.db import engine
from app.main import app
from app.models import Camera, Detection, Organization, User

dt_format = "%Y-%m-%dT%H:%M:%S.%f"

USER_TABLE = [
    {
        "id": 1,
        "organization_id": 1,
        "role": "admin",
        "login": "first_login",
        "hashed_password": "hashed_first_pwd",
        "created_at": datetime.strptime("2024-02-23T08:18:45.447773", dt_format),
    },
    {
        "id": 2,
        "organization_id": 1,
        "role": "agent",
        "login": "second_login",
        "hashed_password": "hashed_second_pwd",
        "created_at": datetime.strptime("2024-02-23T08:18:45.447774", dt_format),
    },
    {
        "id": 3,
        "organization_id": 2,
        "role": "user",
        "login": "third_login",
        "hashed_password": "hashed_third_pwd",
        "created_at": datetime.strptime("2024-02-23T08:18:45.447774", dt_format),
    },
]

ORGANIZATION_TABLE = [
    {
        "id": 1,
        "name": "organization-1",
    },
    {
        "id": 2,
        "name": "organization-2",
    },
]

CAM_TABLE = [
    {
        "id": 1,
        "organization_id": 1,
        "name": "cam-1",
        "angle_of_view": 91.3,
        "elevation": 110.6,
        "lat": 3.6,
        "lon": -45.2,
        "is_trustable": True,
        "last_active_at": datetime.strptime("2023-11-07T15:07:19.226673", dt_format),
        "created_at": datetime.strptime("2023-11-07T15:07:19.226673", dt_format),
    },
    {
        "id": 2,
        "organization_id": 2,
        "name": "cam-2",
        "angle_of_view": 91.3,
        "elevation": 110.6,
        "lat": 3.6,
        "lon": -45.2,
        "is_trustable": False,
        "last_active_at": None,
        "created_at": datetime.strptime("2023-11-07T15:07:19.226673", dt_format),
    },
]

DET_TABLE = [
    {
        "id": 1,
        "camera_id": 1,
        "azimuth": 43.7,
        "bucket_key": "my_file",
        "localization": "xyxy",
        "is_wildfire": True,
        "created_at": datetime.strptime("2023-11-07T15:08:19.226673", dt_format),
        "updated_at": datetime.strptime("2023-11-07T15:08:19.226673", dt_format),
    },
    {
        "id": 2,
        "camera_id": 1,
        "azimuth": 43.7,
        "bucket_key": "my_file",
        "localization": None,
        "is_wildfire": False,
        "created_at": datetime.strptime("2023-11-07T15:08:19.226673", dt_format),
        "updated_at": datetime.strptime("2023-11-07T15:08:19.226673", dt_format),
    },
    {
        "id": 3,
        "camera_id": 2,
        "azimuth": 43.7,
        "bucket_key": "my_file",
        "localization": "[]",
        "is_wildfire": None,
        "created_at": datetime.strptime("2023-11-07T15:08:19.226673", dt_format),
        "updated_at": datetime.strptime("2023-11-07T15:08:19.226673", dt_format),
    },
]


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(  # noqa: S113
        app=app, base_url=f"http://api.localhost:8050{settings.API_V1_STR}", follow_redirects=True
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="function")
async def async_session() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session_maker() as session:
        async with session.begin():
            for table in reversed(SQLModel.metadata.sorted_tables):
                await session.exec(table.delete())
                if hasattr(table.c, "id"):
                    await session.exec(text(f"ALTER SEQUENCE {table.name}_id_seq RESTART WITH 1"))

        yield session
        await session.rollback()


def mock_verify_password(plain_password, hashed_password):
    return hashed_password == f"hashed_{plain_password}"


def mock_hash_password(password):
    return f"hashed_{password}"


@pytest.fixture(scope="session")
def mock_img():
    # Get Pyronear logo
    return requests.get("https://avatars.githubusercontent.com/u/61667887?s=200&v=4", timeout=5).content


@pytest_asyncio.fixture(scope="function")
async def organization_session(async_session: AsyncSession):
    for entry in ORGANIZATION_TABLE:
        async_session.add(Organization(**entry))
    await async_session.commit()
    await async_session.exec(
        text(f"ALTER SEQUENCE organization_id_seq RESTART WITH {max(entry['id'] for entry in ORGANIZATION_TABLE) + 1}")
    )
    await async_session.commit()
    yield async_session
    await async_session.rollback()


@pytest_asyncio.fixture(scope="function")
async def user_session(organization_session: AsyncSession, monkeypatch):
    monkeypatch.setattr(users, "hash_password", mock_hash_password)
    monkeypatch.setattr(login, "verify_password", mock_verify_password)
    for entry in USER_TABLE:
        organization_session.add(User(**entry))
    await organization_session.commit()
    await organization_session.exec(
        text(f"ALTER SEQUENCE user_id_seq RESTART WITH {max(entry['id'] for entry in USER_TABLE) + 1}")
    )
    await organization_session.commit()
    yield organization_session
    await organization_session.rollback()


@pytest_asyncio.fixture(scope="function")
async def camera_session(user_session: AsyncSession, organization_session: AsyncSession):
    for entry in CAM_TABLE:
        user_session.add(Camera(**entry))
    await user_session.commit()
    await user_session.exec(
        text(f"ALTER SEQUENCE camera_id_seq RESTART WITH {max(entry['id'] for entry in CAM_TABLE) + 1}")
    )
    await user_session.commit()
    yield user_session
    await user_session.rollback()


@pytest_asyncio.fixture(scope="function")
async def detection_session(
    user_session: AsyncSession, camera_session: AsyncSession, organization_session: AsyncSession
):
    for entry in DET_TABLE:
        user_session.add(Detection(**entry))
    await user_session.commit()
    # Update the detection index count
    await user_session.exec(
        text(f"ALTER SEQUENCE detection_id_seq RESTART WITH {max(entry['id'] for entry in DET_TABLE) + 1}")
    )
    await user_session.commit()
    yield user_session


def get_token(access_id: int, scopes: str, organizationid: int) -> Dict[str, str]:
    token_data = {"sub": str(access_id), "scopes": scopes, "organization_id": organizationid}
    token = create_access_token(token_data)
    return {"Authorization": f"Bearer {token}"}


def pytest_configure():
    # api.security patching
    pytest.get_token = get_token
    # Table
    pytest.organization_table = [
        {k: datetime.strftime(v, dt_format) if isinstance(v, datetime) else v for k, v in entry.items()}
        for entry in ORGANIZATION_TABLE
    ]
    pytest.user_table = [
        {k: datetime.strftime(v, dt_format) if isinstance(v, datetime) else v for k, v in entry.items()}
        for entry in USER_TABLE
    ]
    pytest.camera_table = [
        {k: datetime.strftime(v, dt_format) if isinstance(v, datetime) else v for k, v in entry.items()}
        for entry in CAM_TABLE
    ]
    pytest.detection_table = [
        {k: datetime.strftime(v, dt_format) if isinstance(v, datetime) else v for k, v in entry.items()}
        for entry in DET_TABLE
    ]
