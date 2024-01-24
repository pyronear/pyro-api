# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from pydantic import Field

from app.models import AccessType

from .base import CredHash, Login, _GroupId, _Id

__all__ = ["AccessRead", "AccessCreation"]


class _AccessBase(Login, _GroupId):
    scope: AccessType = Field(AccessType.user, description="access level")


class AccessCreation(_AccessBase, CredHash):
    pass


class AccessRead(_AccessBase, _Id):
    pass
