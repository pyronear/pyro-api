# Copyright (C) 2020-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from typing import Annotated

from pydantic import BaseModel, Field

from app.models import UserRole

__all__ = ["Cred", "CredHash", "UserCreate", "UserCreation"]


# Accesses
class Login(BaseModel):
    login: Annotated[str, Field(min_length=3, max_length=50, examples=["JohnDoe"])]


class Cred(BaseModel):
    password: Annotated[str, Field(min_length=3, examples=["PickARobustOne"])]


class CredHash(BaseModel):
    hashed_password: str


class Role(BaseModel):
    role: Annotated[UserRole, Field(UserRole.USER)]


class UserCreate(Role):
    login: Annotated[str, Field(min_length=3, max_length=50, examples=["JohnDoe"])]
    password: Annotated[str, Field(min_length=3, examples=["PickARobustOne"])]
    organization_id: Annotated[int, Field(gt=0)]


class UserCreation(Role):
    login: Annotated[str, Field(min_length=3, max_length=50, examples=["JohnDoe"])]
    organization_id: Annotated[int, Field(gt=0)]
