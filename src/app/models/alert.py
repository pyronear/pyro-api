# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["Alert"]


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=True)
    media_id = Column(Integer, ForeignKey("media.id"), nullable=False)
    azimuth = Column(Float(4, asdecimal=True))
    lat = Column(Float(4, asdecimal=True))
    lon = Column(Float(4, asdecimal=True))
    created_at = Column(DateTime, default=func.now())

    device = relationship("Devices", back_populates="alerts")
    event = relationship("Events", back_populates="alerts")
    media = relationship("Media", back_populates="alerts")

    def __repr__(self):
        return f"<Alert(device_id='{self.device_id}', event_id='{self.event_id}', media_id='{self.media_id}'>"
