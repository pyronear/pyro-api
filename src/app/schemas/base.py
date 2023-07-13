# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from datetime import datetime
from typing import Optional

from dateutil.parser import isoparse
from pydantic import BaseModel, Field, field_validator

__all__ = ["Cred", "CredHash", "Login", "Position"]


class _CreatedAt(BaseModel):
    created_at: Optional[datetime] = Field(
        None,
        description="timestamp of entry creation",
        json_schema_extra={"examples": [datetime.utcnow().replace(tzinfo=None)]},
    )

    @field_validator("created_at")
    def validate_created_at(v):
        return datetime.utcnow() if v is None else (isoparse(v) if isinstance(v, str) else v).replace(tzinfo=None)


class _Id(BaseModel):
    id: int = Field(..., gt=0, description="entry unique identifier")


class _GroupId(BaseModel):
    group_id: int = Field(..., gt=0, description="linked group entry")


# Accesses
class Login(BaseModel):
    login: str = Field(
        ...,
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_-]+$",
        description="login of the access",
        json_schema_extra={"examples": ["JohnDoe"]},
    )


class Cred(BaseModel):
    password: str = Field(..., min_length=3, description="password", json_schema_extra={"examples": ["PickARobustOne"]})


class CredHash(BaseModel):
    hashed_password: str = Field(..., description="hashed password")


# Location
class _FlatLocation(BaseModel):
    lat: float = Field(..., gt=-90, lt=90, description="latitude", json_schema_extra={"examples": [44.765181]})
    lon: float = Field(..., gt=-180, lt=180, description="longitude", json_schema_extra={"examples": [4.514880]})


class _Location(_FlatLocation):
    elevation: float = Field(
        ..., gt=0.0, lt=10000, description="number of meters from sea level", json_schema_extra={"examples": [1582]}
    )


class _DefaultLocation(BaseModel):
    lat: Optional[float] = Field(
        None, gt=-90, lt=90, description="latitude", json_schema_extra={"examples": [44.765181]}
    )
    lon: Optional[float] = Field(
        None, gt=-180, lt=180, description="longitude", json_schema_extra={"examples": [4.514880]}
    )
    elevation: Optional[float] = Field(
        None, gt=0.0, lt=10000, description="number of meters from sea level", json_schema_extra={"examples": [1582]}
    )


class _Rotation(BaseModel):
    azimuth: float = Field(
        ...,
        ge=0,
        le=360,
        description="angle between north and direction in degrees",
        json_schema_extra={"examples": [110]},
    )
    pitch: float = Field(..., ge=-90, le=90, json_schema_extra={"examples": [-5]})


class _DefaultRotation(BaseModel):
    azimuth: Optional[float] = Field(
        None,
        ge=0,
        le=360,
        description="angle between north and direction in degrees",
        json_schema_extra={"examples": [110]},
    )
    pitch: Optional[float] = Field(
        None,
        ge=-90,
        le=90,
        description="angle between horizontal plane and direction",
        json_schema_extra={"examples": [-5]},
    )


class DefaultPosition(_DefaultLocation, _DefaultRotation):
    pass


class Position(_Location, _Rotation):
    pass
