# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from pydantic import BaseModel, Field

from .base import _Id

__all__ = ["GroupIn", "GroupOut"]


# Groups
class GroupIn(BaseModel):
    name: str = Field(
        ..., min_length=3, max_length=50, description="name of the group", json_schema_extra={"examples": ["Fireman85"]}
    )


class GroupOut(GroupIn, _Id):
    pass
