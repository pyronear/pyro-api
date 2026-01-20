# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from typing import Annotated

from pydantic import BaseModel, Field

from app.models import Role

__all__ = ["Token", "TokenPayload"]


# Token
class Token(BaseModel):
    access_token: Annotated[
        str,
        Field(
            description="access token",
            json_schema_extra={
                "examples": ["eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.423fgFGTfttrvU6D1k7vF92hH5vaJHCGFYd8E"]
            },
        ),
    ]
    token_type: Annotated[str, Field(description="type of token", json_schema_extra={"examples": ["bearer"]})]


class TokenPayload(BaseModel):
    sub: Annotated[int, Field(gt=0)]
    scopes: Annotated[list[Role], Field(default_factory=list, description="scopes of the token")]
    organization_id: Annotated[int, Field(gt=0)]
