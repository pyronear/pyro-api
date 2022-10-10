# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

__all__ = ["Cred", "CredHash", "Login", "Position"]


class _CreatedAt(BaseModel):
    created_at: Optional[datetime] = None

    @validator("created_at", pre=True, always=True)
    def default_ts_created(v):
        return v or datetime.utcnow()


class _Id(BaseModel):
    id: int = Field(..., gt=0)


class _GroupId(BaseModel):
    group_id: int = Field(..., gt=0)


# Accesses
class Login(BaseModel):
    login: str = Field(..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_-]+$", example="JohnDoe")


class Cred(BaseModel):
    password: str = Field(..., min_length=3, example="PickARobustOne")


class CredHash(BaseModel):
    hashed_password: str


# Location
class _FlatLocation(BaseModel):
    lat: float = Field(..., gt=-90, lt=90, example=44.765181)
    lon: float = Field(..., gt=-180, lt=180, example=4.514880)


class _Location(_FlatLocation):
    elevation: float = Field(..., gt=0.0, lt=10000, example=1582)


class _DefaultLocation(BaseModel):
    lat: Optional[float] = Field(None, gt=-90, lt=90, example=44.765181)
    lon: Optional[float] = Field(None, gt=-180, lt=180, example=4.514880)
    elevation: Optional[float] = Field(None, gt=0.0, lt=10000, example=1582)


class _Rotation(BaseModel):
    azimuth: float = Field(..., ge=0, le=360, example=110)
    pitch: float = Field(..., ge=-90, le=90, example=-5)


class _DefaultRotation(BaseModel):
    azimuth: Optional[float] = Field(None, ge=0, le=360, example=110)
    pitch: Optional[float] = Field(None, ge=-90, le=90, example=-5)


class DefaultPosition(_DefaultLocation, _DefaultRotation):
    pass


class Position(_Location, _Rotation):
    pass
