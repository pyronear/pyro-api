# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List

from pydantic import BaseModel, Field

from app.models import AccessType

__all__ = ["Token", "TokenPayload"]


# Token
class Token(BaseModel):
    access_token: str = Field(
        ...,
        json_schema_extra={"examples": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.423fgFGTfttrvU6D1k7vF92hH5vaJHCGFYd8E"]},
        description="access token",
    )
    token_type: str = Field(..., json_schema_extra={"examples": ["bearer"]}, description="type of token")


class TokenPayload(BaseModel):
    access_id: int = Field(..., gt=0)
    scopes: List[AccessType] = Field([], description="scopes of the token")
