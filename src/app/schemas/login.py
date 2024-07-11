# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from pydantic import BaseModel, Field

from app.models import Role

__all__ = ["Token", "TokenPayload"]


# Token
class Token(BaseModel):
    access_token: str = Field(
        ...,
        description="access token",
        json_schema_extra={"examples": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.423fgFGTfttrvU6D1k7vF92hH5vaJHCGFYd8E"]},
    )
    token_type: str = Field(..., description="type of token", json_schema_extra={"examples": ["bearer"]})


class TokenPayload(BaseModel):
    sub: int = Field(..., gt=0)
    scopes: List[Role] = Field([], description="scopes of the token")
    organization_id: int = Field(..., gt=0)
