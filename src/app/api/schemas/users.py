# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.


from pydantic import Field

from app.db.models import AccessType

from .base import Cred, Login, _CreatedAt, _GroupId, _Id

__all__ = ["UserRead", "UserAuth", "UserCreation"]


class UserRead(Login, _CreatedAt, _Id):
    # Visible info
    pass


class UserAuth(Login, Cred, _GroupId):
    # Authentication request
    scope: AccessType = Field(AccessType.user, description="access level")


class UserCreation(Login):
    # Creation payload
    access_id: int = Field(..., gt=0, description="linked access entry")
