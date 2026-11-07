# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from typing import Union

from sqlmodel.ext.asyncio.session import AsyncSession

from app.core.security import hash_share_token
from app.crud.base import BaseCRUD
from app.models import AlertShare
from app.schemas.shares import ShareCreation, ShareRevocation

__all__ = ["ShareCRUD"]


class ShareCRUD(BaseCRUD[AlertShare, ShareCreation, ShareRevocation]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, AlertShare)

    async def get_by_token(self, token: str) -> Union[AlertShare, None]:
        return await self.get_by("token_hash", hash_share_token(token))
