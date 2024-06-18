# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

import asyncio
import logging

from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.core.security import hash_password
from app.models import Site, User, UserRole

__all__ = ["get_session", "init_db"]

logger = logging.getLogger("uvicorn.error")
engine = AsyncEngine(create_engine(settings.POSTGRES_URL, echo=False))


async def get_session() -> AsyncSession:  # type: ignore[misc]
    async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


async def init_db() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

    async with AsyncSession(engine) as session:
        logger.info("Initializing PostgreSQL database...")

        statement = select(Site).where(Site.name == "pyronear")
        results = await session.execute(statement=statement)
        site = results.scalar_one_or_none()
        if not site:
            new_site = Site(name="pyronear", type="admin")
            session.add(new_site)
            await session.commit()
            await session.refresh(new_site)  # Refresh to get the new site ID
            site_id = new_site.id
        else:
            site_id = site.id

        # Check if admin exists
        statement = select(User).where(User.login == settings.SUPERADMIN_LOGIN)
        results = await session.execute(statement=statement)
        user = results.scalar_one_or_none()
        if not user:
            pwd = hash_password(settings.SUPERADMIN_PWD)
            session.add(
                User(
                    login=settings.SUPERADMIN_LOGIN,
                    hashed_password=pwd,
                    role=UserRole.ADMIN,
                    site_id=site_id,  # Use the correct site_id
                )
            )
        await session.commit()


async def main() -> None:
    await init_db()


if __name__ == "__main__":
    asyncio.run(main())
