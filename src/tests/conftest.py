import asyncio
import io
import os
from datetime import datetime
from typing import AsyncGenerator, Dict, Generator

import pytest
import pytest_asyncio
import requests
from botocore.exceptions import ClientError
from httpx import AsyncClient
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, text
from sqlmodel.ext.asyncio.session import AsyncSession

from app.api.api_v1.endpoints import login, users
from app.core.config import settings
from app.core.security import create_access_token
from app.db import engine
from app.main import app
from app.models import Camera, Detection, Organization, Pose, Sequence, User, Webhook
from app.services.storage import s3_service

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
        "telegram_id": None,
        "slack_hook": None,
    },
    {
        "id": 2,
        "name": "organization-2",
        "telegram_id": None,
        "slack_hook": os.environ["SLACK_HOOK"],
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
        "last_image": None,
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
        "last_image": None,
        "created_at": datetime.strptime("2023-11-07T15:07:19.226673", dt_format),
    },
]

POSE_TABLE = [
    {
        "id": 1,
        "camera_id": 1,
        "azimuth": 45.0,
        "patrol_id": 1,
    },
    {
        "id": 2,
        "camera_id": 1,
        "azimuth": 90.0,
        "patrol_id": 1,
    },
    {
        "id": 3,
        "camera_id": 2,
        "azimuth": 180.0,
        "patrol_id": 1,
    },
]


DET_TABLE = [
    {
        "id": 1,
        "camera_id": 1,
        "pose_id": 1,
        "sequence_id": 1,
        "azimuth": 43.7,
        "bucket_key": "my_file",
        "bboxes": "[(.1,.1,.7,.8,.9)]",
        "created_at": datetime.strptime("2023-11-07T15:08:19.226673", dt_format),
    },
    {
        "id": 2,
        "camera_id": 1,
        "pose_id": 1,
        "sequence_id": 1,
        "azimuth": 43.7,
        "bucket_key": "my_file",
        "bboxes": "[(.1,.1,.7,.8,.9)]",
        "created_at": datetime.strptime("2023-11-07T15:18:19.226673", dt_format),
    },
    {
        "id": 3,
        "camera_id": 1,
        "pose_id": 1,
        "sequence_id": 1,
        "azimuth": 43.7,
        "bucket_key": "my_file",
        "bboxes": "[(.1,.1,.7,.8,.9)]",
        "created_at": datetime.strptime("2023-11-07T15:28:19.226673", dt_format),
    },
    {
        "id": 4,
        "camera_id": 2,
        "pose_id": 3,
        "sequence_id": 2,
        "azimuth": 74.8,
        "bucket_key": "my_file",
        "bboxes": "[(.1,.1,.7,.8,.9)]",
        "created_at": datetime.strptime("2023-11-07T16:08:19.226673", dt_format),
    },
]

SEQ_TABLE = [
    {
        "id": 1,
        "camera_id": 1,
        "pose_id": 1,
        "azimuth": 43.7,
        "is_wildfire": "wildfire_smoke",
        "cone_azimuth": 34.6,
        "cone_angle": 54.8,
        "started_at": datetime.strptime("2023-11-07T15:08:19.226673", dt_format),
        "last_seen_at": datetime.strptime("2023-11-07T15:28:19.226673", dt_format),
    },
    {
        "id": 2,
        "camera_id": 2,
        "pose_id": 3,
        "azimuth": 74.8,
        "is_wildfire": None,
        "cone_azimuth": 65.7,
        "cone_angle": 54.8,
        "started_at": datetime.strptime("2023-11-07T16:08:19.226673", dt_format),
        "last_seen_at": datetime.strptime("2023-11-07T16:08:19.226673", dt_format),
    },
]

WEBHOOK_TABLE = [
    {
        "id": 1,
        "url": f"http://localhost:8050{settings.API_V1_STR}",
    },
    {
        "id": 2,
        "url": "http://localhost:9999",
    },
]


@pytest.fixture(scope="session")
def event_loop(request) -> Generator:
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(
        app=app, base_url=f"http://api.localhost:8050{settings.API_V1_STR}", follow_redirects=True, timeout=5
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
        text(
            f"ALTER SEQUENCE {Organization.__tablename__}_id_seq RESTART WITH {max(entry['id'] for entry in ORGANIZATION_TABLE) + 1}"
        )
    )
    await async_session.commit()
    # Create buckets
    for entry in ORGANIZATION_TABLE:
        s3_service.create_bucket(s3_service.resolve_bucket_name(entry["id"]))
    yield async_session
    await async_session.rollback()
    # Delete buckets
    try:
        for entry in ORGANIZATION_TABLE:
            await s3_service.delete_bucket(s3_service.resolve_bucket_name(entry["id"]))
    except ValueError:
        pass


@pytest_asyncio.fixture(scope="function")
async def webhook_session(async_session: AsyncSession):
    for entry in WEBHOOK_TABLE:
        async_session.add(Webhook(**entry))
    await async_session.commit()
    await async_session.exec(
        text(
            f"ALTER SEQUENCE {Webhook.__tablename__}_id_seq RESTART WITH {max(entry['id'] for entry in WEBHOOK_TABLE) + 1}"
        )
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
        text(f"ALTER SEQUENCE {User.__tablename__}_id_seq RESTART WITH {max(entry['id'] for entry in USER_TABLE) + 1}")
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
        text(f"ALTER SEQUENCE {Camera.__tablename__}_id_seq RESTART WITH {max(entry['id'] for entry in CAM_TABLE) + 1}")
    )
    await user_session.commit()
    yield user_session
    await user_session.rollback()


@pytest_asyncio.fixture(scope="function")
async def pose_session(camera_session: AsyncSession):
    for entry in POSE_TABLE:
        camera_session.add(Pose(**entry))
    await camera_session.commit()
    await camera_session.exec(
        text(f"ALTER SEQUENCE {Pose.__tablename__}_id_seq RESTART WITH {max(entry['id'] for entry in POSE_TABLE) + 1}")
    )
    await camera_session.commit()
    yield camera_session
    await camera_session.rollback()


@pytest_asyncio.fixture(scope="function")
async def sequence_session(pose_session: AsyncSession):
    for entry in SEQ_TABLE:
        pose_session.add(Sequence(**entry))
    await pose_session.commit()
    await pose_session.exec(
        text(
            f"ALTER SEQUENCE {Sequence.__tablename__}_id_seq RESTART WITH {max(entry['id'] for entry in SEQ_TABLE) + 1}"
        )
    )
    await pose_session.commit()
    yield pose_session
    await pose_session.rollback()


@pytest_asyncio.fixture(scope="function")
async def detection_session(pose_session: AsyncSession, sequence_session: AsyncSession):
    for entry in DET_TABLE:
        sequence_session.add(Detection(**entry))
    await sequence_session.commit()
    # Update the detection index count
    await sequence_session.exec(
        text(
            f"ALTER SEQUENCE {Detection.__tablename__}_id_seq RESTART WITH {max(entry['id'] for entry in DET_TABLE) + 1}"
        )
    )
    await sequence_session.commit()
    # Create bucket files
    for entry in DET_TABLE:
        bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(entry["camera_id"]))
        bucket.upload_file(entry["bucket_key"], io.BytesIO(b""))
    yield sequence_session
    await sequence_session.rollback()
    # Delete bucket files
    try:
        for entry in DET_TABLE:
            bucket = s3_service.get_bucket(s3_service.resolve_bucket_name(entry["camera_id"]))
            bucket.delete_file(entry["bucket_key"])
    except ClientError:
        pass


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
    pytest.pose_table = [
        {k: datetime.strftime(v, dt_format) if isinstance(v, datetime) else v for k, v in entry.items()}
        for entry in POSE_TABLE
    ]
    pytest.detection_table = [
        {k: datetime.strftime(v, dt_format) if isinstance(v, datetime) else v for k, v in entry.items()}
        for entry in DET_TABLE
    ]
    pytest.sequence_table = [
        {k: datetime.strftime(v, dt_format) if isinstance(v, datetime) else v for k, v in entry.items()}
        for entry in SEQ_TABLE
    ]
    pytest.webhook_table = [
        {k: datetime.strftime(v, dt_format) if isinstance(v, datetime) else v for k, v in entry.items()}
        for entry in WEBHOOK_TABLE
    ]
