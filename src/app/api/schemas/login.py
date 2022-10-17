# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from typing import List, Optional

from pydantic import BaseModel, Field

from app.db.models import AccessType

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
