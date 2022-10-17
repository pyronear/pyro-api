# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.


from pydantic import BaseModel, Field

from .base import _Id

__all__ = ["GroupIn", "GroupOut"]


# Groups
class GroupIn(BaseModel):
    name: str = Field(..., min_length=3, max_length=50, example="Fireman85", description="name of the group")


class GroupOut(GroupIn, _Id):
    pass
