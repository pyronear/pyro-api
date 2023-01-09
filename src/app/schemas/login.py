# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List, Optional

from pydantic import BaseModel, Field

from app.models import AccessType

__all__ = ["Token", "TokenPayload"]


# Token
class Token(BaseModel):
    access_token: str = Field(
        ...,
        example="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.423fgFGTfttrvU6D1k7vF92hH5vaJHCGFYd8E",
        description="access token",
    )
    token_type: str = Field(..., example="bearer", description="type of token")


class TokenPayload(BaseModel):
    user_id: Optional[str] = Field(None, description="linked user entry")
    scopes: List[AccessType] = Field([], description="scopes of the token")
