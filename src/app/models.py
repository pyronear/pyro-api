# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from enum import Enum
from typing import Union

from sqlmodel import Field, SQLModel

from app.core.config import settings

__all__ = ["Alert", "AlertSequence", "Camera", "Detection", "Organization", "Pose", "Sequence", "User"]


class UserRole(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    USER = "user"


class Role(str, Enum):
    ADMIN = "admin"
    AGENT = "agent"
    CAMERA = "camera"
    USER = "user"


class AnnotationType(str, Enum):
    WILDFIRE_SMOKE = "wildfire_smoke"
    OTHER_SMOKE = "other_smoke"
    OTHER = "other"


class User(SQLModel, table=True):
    __tablename__ = "users"
    id: int = Field(None, primary_key=True)
    organization_id: int = Field(..., foreign_key="organizations.id", nullable=False)
    role: UserRole = Field(UserRole.USER, nullable=False)
    # Allow sign-up/in via login + password
    login: str = Field(..., index=True, unique=True, min_length=2, max_length=50, nullable=False)
    hashed_password: str = Field(..., min_length=5, max_length=70, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Camera(SQLModel, table=True):
    __tablename__ = "cameras"
    id: int = Field(None, primary_key=True)
    organization_id: int = Field(..., foreign_key="organizations.id", nullable=False)
    name: str = Field(..., min_length=5, max_length=100, nullable=False, unique=True)
    angle_of_view: float = Field(..., gt=0, le=360, nullable=False)
    elevation: float = Field(..., gt=0, lt=10000, nullable=False)
    lat: float = Field(..., gt=-90, lt=90)
    lon: float = Field(..., gt=-180, lt=180)
    is_trustable: bool = True
    last_active_at: Union[datetime, None] = None
    last_image: Union[str, None] = None
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Pose(SQLModel, table=True):
    __tablename__ = "poses"
    id: int = Field(default=None, primary_key=True)
    camera_id: int = Field(..., foreign_key="cameras.id", nullable=False)
    azimuth: float = Field(..., ge=0, lt=360)
    patrol_id: int | None = Field(default=None, max_length=100)


class OcclusionMask(SQLModel, table=True):
    __tablename__ = "occlusion_masks"
    id: int = Field(default=None, primary_key=True)
    pose_id: int = Field(..., foreign_key="poses.id", nullable=False)
    mask: str = Field(..., min_length=2, max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Detection(SQLModel, table=True):
    __tablename__ = "detections"
    id: int = Field(None, primary_key=True)
    camera_id: int = Field(..., foreign_key="cameras.id", nullable=False)
    pose_id: Union[int, None] = Field(None, foreign_key="poses.id", nullable=True)
    sequence_id: Union[int, None] = Field(None, foreign_key="sequences.id", nullable=True)
    bucket_key: str
    bboxes: str = Field(..., min_length=2, max_length=settings.MAX_BBOX_STR_LENGTH, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)


class Sequence(SQLModel, table=True):
    __tablename__ = "sequences"
    id: int = Field(None, primary_key=True)
    camera_id: int = Field(..., foreign_key="cameras.id", nullable=False)
    pose_id: Union[int, None] = Field(None, foreign_key="poses.id", nullable=True)
    camera_azimuth: float = Field(..., ge=0, lt=360)
    is_wildfire: Union[AnnotationType, None] = None
    sequence_azimuth: Union[float, None] = Field(None, nullable=True)
    cone_angle: Union[float, None] = Field(None, nullable=True)
    started_at: datetime = Field(..., nullable=False)
    last_seen_at: datetime = Field(..., nullable=False)


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"
    id: int = Field(None, primary_key=True)
    organization_id: int = Field(..., foreign_key="organizations.id", nullable=False)
    lat: Union[float, None] = Field(default=None, gt=-90, lt=90, nullable=True)
    lon: Union[float, None] = Field(default=None, gt=-180, lt=180, nullable=True)
    started_at: datetime = Field(..., nullable=False)
    last_seen_at: datetime = Field(..., nullable=False)


class AlertSequence(SQLModel, table=True):
    __tablename__ = "alerts_sequences"
    alert_id: int = Field(primary_key=True, foreign_key="alerts.id")
    sequence_id: int = Field(primary_key=True, foreign_key="sequences.id")


class Organization(SQLModel, table=True):
    __tablename__ = "organizations"
    id: int = Field(None, primary_key=True)
    name: str = Field(..., min_length=5, max_length=100, nullable=False, unique=True)
    telegram_id: Union[str, None] = Field(None, nullable=True)
    slack_hook: Union[str, None] = Field(None, nullable=True)


class Webhook(SQLModel, table=True):
    __tablename__ = "webhooks"
    id: int = Field(None, primary_key=True)
    url: str = Field(..., nullable=False, unique=True)
