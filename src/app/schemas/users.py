# Copyright (C) 2020-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from pydantic import BaseModel, Field

from app.models import UserRole

__all__ = ["Cred", "CredHash", "UserCreate", "UserCreation"]


# Accesses
class Login(BaseModel):
    login: str = Field(..., min_length=3, max_length=50, examples=["JohnDoe"])


class Cred(BaseModel):
    password: str = Field(..., min_length=3, examples=["PickARobustOne"])


class CredHash(BaseModel):
    hashed_password: str


class Role(BaseModel):
    role: UserRole = Field(UserRole.USER)


class UserCreate(Role):
    login: str = Field(..., min_length=3, max_length=50, examples=["JohnDoe"])
    password: str = Field(..., min_length=3, examples=["PickARobustOne"])
    organization_id: int = Field(..., gt=0)


class UserCreation(Role):
    login: str = Field(..., min_length=3, max_length=50, examples=["JohnDoe"])
