# Copyright (C) 2021-2022, Pyronear.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator

__all__ = ["Cred", "CredHash", "Login", "Position"]


class _CreatedAt(BaseModel):
    created_at: Optional[datetime] = Field(None, description="timestamp of entry creation")

    @validator("created_at", pre=True, always=True)
    def default_ts_created(v):
        return v or datetime.utcnow()


class _Id(BaseModel):
    id: int = Field(..., gt=0, description="entry unique identifier")


class _GroupId(BaseModel):
    group_id: int = Field(..., gt=0, description="linked group entry")


# Accesses
class Login(BaseModel):
    login: str = Field(
        ..., min_length=3, max_length=50, regex="^[a-zA-Z0-9_-]+$", example="JohnDoe", description="login of the access"
    )


class Cred(BaseModel):
    password: str = Field(..., min_length=3, example="PickARobustOne", description="password")


class CredHash(BaseModel):
    hashed_password: str = Field(..., description="hashed password")


# Location
class _FlatLocation(BaseModel):
    lat: float = Field(..., gt=-90, lt=90, example=44.765181, description="latitude")
    lon: float = Field(..., gt=-180, lt=180, example=4.514880, description="longitude")


class _Location(_FlatLocation):
    elevation: float = Field(..., gt=0.0, lt=10000, example=1582, description="number of meters from sea level")


class _DefaultLocation(BaseModel):
    lat: Optional[float] = Field(None, gt=-90, lt=90, example=44.765181, description="latitude")
    lon: Optional[float] = Field(None, gt=-180, lt=180, example=4.514880, description="longitude")
    elevation: Optional[float] = Field(
        None, gt=0.0, lt=10000, example=1582, description="number of meters from sea level"
    )


class _Rotation(BaseModel):
    azimuth: float = Field(..., ge=0, le=360, example=110, description="angle between north and direction in degrees")
    pitch: float = Field(..., ge=-90, le=90, example=-5)


class _DefaultRotation(BaseModel):
    azimuth: Optional[float] = Field(
        None, ge=0, le=360, example=110, description="angle between north and direction in degrees"
    )
    pitch: Optional[float] = Field(
        None, ge=-90, le=90, example=-5, description="angle between horizontal plane and direction"
    )


class DefaultPosition(_DefaultLocation, _DefaultRotation):
    pass


class Position(_Location, _Rotation):
    pass
