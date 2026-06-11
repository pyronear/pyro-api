# Copyright (C) 2024-2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from enum import Enum
from typing import Union

from sqlmodel import Field, SQLModel

from app.core.config import settings
from app.core.time import utcnow

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
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


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
    created_at: datetime = Field(default_factory=utcnow, nullable=False)
    # Device connection — never exposed in public API responses
    camera_ip: Union[str, None] = Field(default=None, nullable=True)
    device_ip: Union[str, None] = Field(default=None, nullable=True)


class Pose(SQLModel, table=True):
    __tablename__ = "poses"
    id: int = Field(default=None, primary_key=True)
    camera_id: int = Field(..., foreign_key="cameras.id", nullable=False)
    azimuth: float = Field(..., ge=0, lt=360)
    patrol_id: int | None = Field(default=None, max_length=100)
    active: bool = Field(default=True, nullable=False)
    image: Union[str, None] = None


class OcclusionMask(SQLModel, table=True):
    __tablename__ = "occlusion_masks"
    id: int = Field(default=None, primary_key=True)
    pose_id: int = Field(..., foreign_key="poses.id", nullable=False)
    mask: str = Field(..., min_length=2, max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


class Detection(SQLModel, table=True):
    __tablename__ = "detections"
    id: int = Field(None, primary_key=True)
    camera_id: int = Field(..., foreign_key="cameras.id", nullable=False)
    pose_id: int = Field(..., foreign_key="poses.id", nullable=False)
    sequence_id: Union[int, None] = Field(None, foreign_key="sequences.id", nullable=True)
    bucket_key: str
    crop_bucket_key: Union[str, None] = Field(default=None, nullable=True)
    bbox: str = Field(..., min_length=2, max_length=settings.MAX_BBOX_STR_LENGTH_SINGLE, nullable=False)
    others_bboxes: Union[str, None] = Field(default=None, max_length=settings.MAX_BBOX_STR_LENGTH_OTHERS, nullable=True)
    created_at: datetime = Field(default_factory=utcnow, nullable=False)


# sequences.validation_status values — the single source of truth (enforced by a DB CHECK
# constraint; the worker and the CRUD queue guards both import from here).
VALIDATED_BY_MODEL = "model"
FAIL_OPEN_UNAVAILABLE = "fail_open_unavailable"
FAIL_OPEN_STALE = "fail_open_stale"
WINDOW_EXHAUSTED = "window_exhausted"
VALIDATION_FAILED = "failed"
# Terminal states: the queue must never resurrect these.
TERMINAL_VALIDATION_STATUSES = (WINDOW_EXHAUSTED, VALIDATION_FAILED)


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
    max_conf: Union[float, None] = Field(
        None,
        nullable=True,
        description=(
            "Highest detection confidence ever attached to this sequence. "
            "Monotonic: not recomputed downward when detections are deleted or reassigned."
        ),
    )
    temporal_model_score: Union[float, None] = Field(
        None,
        nullable=True,
        description="Latest temporal-model smoke probability for this sequence, or None if never scored.",
    )
    # Provenance of temporal_model_score, written in the same UPDATE: lets stored scores be
    # evaluated per model release / serving image (e.g. against is_wildfire annotations)
    # long after redeploys. None when never scored, or when the serving build is unstamped.
    temporal_model_version: Union[str, None] = Field(
        None,
        nullable=True,
        max_length=32,
        description="Model release that produced temporal_model_score (manifest version, e.g. '0.1.0').",
    )
    temporal_api_version: Union[str, None] = Field(
        None,
        nullable=True,
        max_length=32,
        description="Temporal API serving-code version (Docker image tag) that produced temporal_model_score.",
    )
    is_validated: bool = Field(
        default=False,
        nullable=False,
        description=(
            "Whether the sequence passed validation (risk gate + temporal model, or fail-open). "
            "Only validated sequences are triangulated and notified."
        ),
    )
    # The three validation-job fields below are internal plumbing (the DB-backed queue);
    # they are excluded from API serialization.
    validation_due_at: Union[datetime, None] = Field(
        None,
        nullable=True,
        exclude=True,
        description=(
            "When set, the sequence is queued for temporal validation (set on each new detection, "
            "kept at its oldest value while queued so ordering is FIFO). Cleared once the worker "
            "reaches a verdict for the current frame set or a terminal state."
        ),
    )
    validation_lease_until: Union[datetime, None] = Field(
        None,
        nullable=True,
        exclude=True,
        description=(
            "Lease claimed by the validation worker processing this sequence; other workers skip "
            "the row until it expires. An expired lease with validation_due_at still set means the "
            "worker died mid-job and the job is up for grabs again."
        ),
    )
    validation_status: Union[str, None] = Field(
        None,
        nullable=True,
        max_length=32,
        exclude=True,
        description=(
            "How validation concluded: 'model' (temporal model confirmed), 'fail_open_unavailable' "
            "(model unreachable/breaker open), 'fail_open_stale' (queued past the max age), "
            "'window_exhausted' (scored but never confirmed within the frame window; terminal), "
            "'failed' (gave up after repeated job errors; terminal). NULL while pending or for "
            "pre-gate sequences. Allowed values are enforced by a DB CHECK constraint."
        ),
    )
    validation_attempts: int = Field(
        default=0,
        nullable=False,
        exclude=True,
        description=(
            "Consecutive errored validation runs for this sequence (reset on every completed "
            "job). At MAX_VALIDATION_ATTEMPTS the job dead-letters as validation_status='failed' "
            "instead of retrying forever."
        ),
    )


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
