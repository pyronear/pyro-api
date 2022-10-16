# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from pydantic import Field

from app.db.models import AccessType

from .base import CredHash, Login, _GroupId, _Id

__all__ = ["AccessRead", "AccessCreation"]


class _AccessBase(Login, _GroupId):
    scope: AccessType = Field(AccessType.user, description="access level")


class AccessCreation(_AccessBase, CredHash):
    pass


class AccessRead(_AccessBase, _Id):
    pass
