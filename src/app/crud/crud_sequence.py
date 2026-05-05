# Copyright (C) 2025-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.


from typing import Any, Union, cast

from sqlalchemy import case, or_, update
from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Sequence
from app.schemas.sequences import SequenceLabel, SequenceUpdate

__all__ = ["SequenceCRUD"]


class SequenceCRUD(BaseCRUD[Sequence, Sequence, Union[SequenceUpdate, SequenceLabel]]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Sequence)

    async def bump_max_conf(self, sequence_id: int, candidate: float) -> None:
        """Atomically raise sequences.max_conf to candidate if higher (or set if NULL).

        Uses a portable CASE expression so it runs on SQLite as well as Postgres.
        """
        max_conf_col = cast(Any, Sequence.max_conf)
        bumped: Any = cast(Any, case)(
            (or_(max_conf_col.is_(None), max_conf_col < candidate), candidate),
            else_=max_conf_col,
        )
        stmt: Any = update(Sequence).where(cast(Any, Sequence.id) == sequence_id).values(max_conf=bumped)
        await self.session.exec(stmt)
        await self.session.commit()
