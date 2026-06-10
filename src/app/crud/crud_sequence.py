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

    async def set_temporal_score(self, sequence_id: int, score: float) -> None:
        """Persist the latest temporal-model score for the sequence."""
        stmt: Any = update(Sequence).where(cast(Any, Sequence.id) == sequence_id).values(temporal_model_score=score)
        await self.session.exec(stmt)
        await self.session.commit()

    async def claim_validation(self, sequence_id: int) -> bool:
        """Atomically flip ``is_validated`` from False to True.

        Returns True only for the caller that won the flip, so concurrent background tasks
        for the same sequence don't both triangulate and notify.
        """
        id_col = cast(Any, Sequence.id)
        validated_col = cast(Any, Sequence.is_validated)
        stmt: Any = update(Sequence)
        stmt = stmt.where(id_col == sequence_id).where(validated_col.is_(False)).values(is_validated=True)
        result = await self.session.exec(stmt)
        await self.session.commit()
        return bool(getattr(result, "rowcount", 0))

    async def release_validation(self, sequence_id: int) -> None:
        """Flip ``is_validated`` back to False so a later detection can retry the claim.

        Used when post-claim work (alert attachment) fails: without the release, the
        sequence would stay validated-but-never-alerted forever.
        """
        stmt: Any = update(Sequence).where(cast(Any, Sequence.id) == sequence_id).values(is_validated=False)
        await self.session.exec(stmt)
        await self.session.commit()
