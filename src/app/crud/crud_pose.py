# Copyright (C) 2024-2025, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Pose
from app.schemas.poses import PoseCreate, PoseUpdate

__all__ = ["PoseCRUD"]


class PoseCRUD(BaseCRUD[Pose, PoseCreate, PoseUpdate]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Pose)
