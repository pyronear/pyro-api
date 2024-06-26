# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details

from datetime import datetime, timedelta
from typing import List, Optional, Tuple

from sqlmodel import and_, desc, select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.config import settings
from app.crud.base import BaseCRUD
from app.models import Wildfire
from app.schemas.wildfires import WildfireCreate, WildfireUpdate

__all__ = ["WildfireCRUD"]


class WildfireCRUD(BaseCRUD[Wildfire, WildfireCreate, WildfireUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Wildfire)

    async def get_ending_time_null(self, camera_id: int) -> List[Wildfire]:
        statement = select(Wildfire).where(Wildfire.camera_id == camera_id).where(Wildfire.ending_time == None)  # type: ignore # noqa: E711
        result = await self.session.execute(statement)
        return result.scalars().all()

    async def resolve_previous_wildfire(self, camera_id: int) -> Optional[Wildfire]:
        # check whether there is a wildfire in the last 30 min by the same device
        max_ts = datetime.utcnow() - timedelta(seconds=settings.ALERT_RELAXATION_SECONDS)
        statement = (
            select(Wildfire)  # type: ignore[var-annotated]
            .where(and_(Wildfire.camera_id == camera_id, Wildfire.starting_time >= max_ts))
            .order_by(desc(Wildfire.starting_time))
            .limit(1)
        )

        result = await self.session.execute(statement)
        return result.scalar()

    async def create_or_update_wildfire(self, payload: WildfireCreate) -> Tuple[Optional[int], bool]:
        """Return the id of wildfire created or updated and a boolean flag to tell if a new event was created

        Args:
            payload: alert object

        Returns: tuple (int, bool) -> (event_id, new alert ?)
        """
        # check whether there is a wildfire in the last 30 min by the same device
        previous_wildfire = await self.resolve_previous_wildfire(payload.camera_id)
        if previous_wildfire is None:
            wildfire = await self.create(payload)
            return wildfire.id, True
        return previous_wildfire.id, False
