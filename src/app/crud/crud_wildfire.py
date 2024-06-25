# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Wildfire
from app.schemas.wildfires import WildfireCreate, WildfireUpdate

__all__ = ["WildfireCRUD"]


class WildfireCRUD(BaseCRUD[Wildfire, WildfireCreate, WildfireUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Wildfire)

    async def get_ending_time_null(self, camera_id: int) -> List[Wildfire]:
        statement = select(Wildfire).where(Wildfire.camera_id == camera_id).where(Wildfire.ending_time is None)  # type: ignore[var-annotated]
        result = await self.session.execute(statement)
        return result.scalars().all()
