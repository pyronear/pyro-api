# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Any, Union, cast

from sqlalchemy import desc
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Detection
from app.schemas.detections import EMPTY_BBOXES, DetectionCreate, DetectionSequence

__all__ = ["DetectionCRUD"]


class DetectionCRUD(BaseCRUD[Detection, DetectionCreate, DetectionSequence]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Detection)

    async def get_latest_with_bbox(self, sequence_id: int) -> Union[Detection, None]:
        """Latest detection of the sequence carrying a real bbox (continuity rows excluded)."""
        statement: Any = (
            select(Detection)
            .where(cast(Any, Detection.sequence_id) == sequence_id)
            .where(cast(Any, Detection.bbox) != EMPTY_BBOXES)
            .order_by(desc(cast(Any, Detection.created_at)))
            .limit(1)
        )
        results = await self.session.exec(statement)
        return results.first()
