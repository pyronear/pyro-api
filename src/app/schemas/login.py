# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import List, Literal

from pydantic import BaseModel, ConfigDict, Field

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
    model_config = ConfigDict(coerce_numbers_to_str=True)

    sub: str = Field(..., min_length=1, description="Keycloak user id, or the user/camera id for API-issued tokens")
    scopes: List[Role] = Field([], description="scopes of the token")
    organization_id: int = Field(..., gt=0)
    auth_source: Literal["keycloak", "api"] = Field("api", description="issuer of the token")

    @property
    def is_admin(self) -> bool:
        return Role.ADMIN in self.scopes

    @property
    def camera_id(self) -> int:
        """Camera tokens are API-issued with the camera id as subject."""
        if Role.CAMERA not in self.scopes:
            raise ValueError("camera_id is only defined for camera tokens")
        return int(self.sub)
