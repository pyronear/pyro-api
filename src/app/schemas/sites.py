# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from pydantic import BaseModel, Field

__all__ = ["SiteCreate"]


class SiteCreate(BaseModel):
    site_id: int = Field(..., gt=0)
