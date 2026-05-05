# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import Any, Union, cast

from sqlalchemy import func, update
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Sequence
from app.schemas.sequences import SequenceLabel, SequenceUpdate

__all__ = ["SequenceCRUD"]


class SequenceCRUD(BaseCRUD[Sequence, Sequence, Union[SequenceUpdate, SequenceLabel]]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Sequence)

    async def bump_max_conf(self, sequence_id: int, candidate: float) -> None:
        """Atomically raise sequences.max_conf to candidate if higher (or set if NULL)."""
        stmt: Any = (
            update(Sequence)
            .where(cast(Any, Sequence.id) == sequence_id)
            .values(max_conf=func.greatest(func.coalesce(Sequence.max_conf, candidate), candidate))
        )
        await self.session.exec(stmt)
        await self.session.commit()
