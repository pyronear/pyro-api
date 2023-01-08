# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


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
