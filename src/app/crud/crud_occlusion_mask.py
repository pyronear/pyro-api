# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.models import OcclusionMask
from app.schemas.occlusion_masks import OcclusionMaskCreate, OcclusionMaskUpdate

__all__ = ["OcclusionMaskCRUD"]


class OcclusionMaskCRUD(BaseCRUD[OcclusionMask, OcclusionMaskCreate, OcclusionMaskUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, OcclusionMask)

    async def get_by_pose(self, pose_id: int) -> List[OcclusionMask]:
        results = await self.session.exec(select(OcclusionMask).where(OcclusionMask.pose_id == pose_id))
        return results.all()
