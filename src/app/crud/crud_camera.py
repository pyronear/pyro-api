# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from sqlmodel.ext.asyncio.session import AsyncSession

from app.crud.base import BaseCRUD
from app.models import Camera
from app.schemas.cameras import LastActive

__all__ = ["CameraCRUD"]


class CameraCRUD(BaseCRUD[Camera, Camera, LastActive]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session, Camera)
