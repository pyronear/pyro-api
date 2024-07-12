# Copyright (C) 2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from enum import Enum
from typing import Union

from sqlmodel import Field, SQLModel

__all__ = ["Camera", "Detection", "Organization", "User"]


class UserRole(str, Enum):
    ADMIN: str = "admin"
    AGENT: str = "agent"
    USER: str = "user"


class Role(str, Enum):
    ADMIN: str = "admin"
    AGENT: str = "agent"
    CAMERA: str = "camera"
    USER: str = "user"


class User(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    organization_id: int = Field(..., foreign_key="organization.id", nullable=False)
    role: UserRole = Field(UserRole.USER, nullable=False)
    # Allow sign-up/in via login + password
    login: str = Field(..., index=True, unique=True, min_length=2, max_length=50, nullable=False)
    hashed_password: str = Field(..., min_length=5, max_length=70, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Camera(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    organization_id: int = Field(..., foreign_key="organization.id", nullable=False)
    name: str = Field(..., min_length=5, max_length=100, nullable=False, unique=True)
    angle_of_view: float = Field(..., gt=0, le=360, nullable=False)
    elevation: float = Field(..., gt=0, lt=10000, nullable=False)
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)
    is_trustable: bool = True
    last_active_at: Union[datetime, None] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Detection(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    camera_id: int = Field(..., foreign_key="camera.id", nullable=False)
    azimuth: float = Field(..., gt=0, lt=360)
    bucket_key: str
    localization: Union[str, None]
    is_wildfire: Union[bool, None] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    updated_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Organization(SQLModel, table=True):
    id: int = Field(None, primary_key=True)
    name: str = Field(..., min_length=5, max_length=100, nullable=False, unique=True)
