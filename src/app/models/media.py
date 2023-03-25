# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["MediaType", "Media"]


class MediaType(str, enum.Enum):
    image: str = "image"
    video: str = "video"


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    bucket_key = Column(String(100), nullable=True)
    type = Column(Enum(MediaType), default=MediaType.image)
    created_at = Column(DateTime, default=func.now())

    device = relationship("Device", uselist=False, back_populates="media")
    alerts = relationship("Alert", back_populates="media")

    def __repr__(self):
        return f"<Media(device_id='{self.device_id}', bucket_key='{self.bucket_key}', type='{self.type}'>"
