# Copyright (C) 2024-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import asyncio
import logging
from typing import Any

from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlmodel import SQLModel, create_engine, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models import Organization, User, UserRole
from app.services.storage import s3_service

__all__ = ["get_session", "init_db"]

logger = logging.getLogger("uvicorn.error")
engine = AsyncEngine(create_engine(settings.POSTGRES_URL, echo=False))


async def get_session() -> AsyncSession:  # type: ignore[misc]
    async_session = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        logger.info("Initializing PostgreSQL database...")

        # Create the superadmin organization
        org_stmt: Any = select(Organization).where(Organization.name == settings.SUPERADMIN_ORG)
        org_results = await session.exec(statement=org_stmt)
        organization = org_results.one_or_none()
        if not organization:
            new_orga = Organization(name=settings.SUPERADMIN_ORG)
            session.add(new_orga)
            await session.commit()
            await session.refresh(new_orga)  # Refresh to get the new organization ID
            organization_id = new_orga.id
        else:
            organization_id = organization.id
        # Create the bucket
        s3_service.create_bucket(s3_service.resolve_bucket_name(organization_id))

        # Check if admin exists
        user_stmt: Any = select(User).where(User.login == settings.SUPERADMIN_LOGIN)
        user_results = await session.exec(statement=user_stmt)
        user = user_results.one_or_none()
        if not user:
            pwd = hash_password(settings.SUPERADMIN_PWD)
            session.add(
                User(
                    login=settings.SUPERADMIN_LOGIN,
                    hashed_password=pwd,
                    role=UserRole.ADMIN,
                    organization_id=organization_id,
                )
            )
        await session.commit()


async def main() -> None:
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())
