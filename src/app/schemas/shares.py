# Copyright (C) 2026, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0> for full license details.

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field

__all__ = [
    "ShareCreate",
    "ShareCreated",
    "ShareCreation",
    "ShareRead",
    "ShareRevocation",
    "ShareStatus",
    "SharedAlertRead",
    "SharedCameraRead",
    "SharedDetectionRead",
    "SharedSequenceRead",
]


class ShareStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


class ShareCreate(BaseModel):
    alert_id: int = Field(..., gt=0)


class ShareCreation(BaseModel):
    alert_id: int = Field(..., gt=0)
    organization_id: int = Field(..., gt=0)
    created_by: Optional[int] = Field(None, gt=0)
    token_hash: str = Field(..., min_length=64, max_length=64)
    expires_at: datetime


class ShareRevocation(BaseModel):
    revoked_at: datetime


class ShareCreated(BaseModel):
    share_id: int
    alert_id: int
    token: str = Field(..., description="secret of the public link, returned only once")
    expires_at: datetime


class ShareRead(BaseModel):
    id: int
    alert_id: int
    organization_id: int
    created_by: Optional[int] = None
    created_at: datetime
    expires_at: datetime
    revoked_at: Optional[datetime] = None
    status: ShareStatus


# Public projection: explicit whitelists, so no internal field (ids, device IPs, labels,
# validation plumbing) reaches someone without an account.
class SharedCameraRead(BaseModel):
    name: str
    lat: float
    lon: float
    elevation: float
    angle_of_view: float


class SharedDetectionRead(BaseModel):
    recorded_at: datetime
    bbox: str
    url: str = Field(..., description="temporary URL to access the media content")


class SharedSequenceRead(BaseModel):
    started_at: datetime
    last_seen_at: datetime
    camera_azimuth: float
    sequence_azimuth: Optional[float] = None
    cone_angle: Optional[float] = None
    camera: SharedCameraRead
    detections: List[SharedDetectionRead] = Field(default_factory=list)


class SharedAlertRead(BaseModel):
    started_at: datetime
    last_seen_at: datetime
    lat: Optional[float] = Field(None, description="estimated fire position, if triangulated")
    lon: Optional[float] = Field(None, description="estimated fire position, if triangulated")
    expires_at: datetime
    sequences: List[SharedSequenceRead] = Field(default_factory=list)
