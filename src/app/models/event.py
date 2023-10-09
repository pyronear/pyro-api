# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import enum

from sqlalchemy import Boolean, Column, DateTime, Enum, Float, ForeignKey, Integer
from sqlalchemy.orm import RelationshipProperty, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["EventType", "Event"]


class EventType(str, enum.Enum):
    wildfire: str = "wildfire"
    domestic_fire: str = "domestic fire"
    chimney: str = "chimney"
    cloud: str = "cloud"
    other: str = "other"
    undefined: str = "undefined"


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    lat = Column(Float(4, asdecimal=True))
    lon = Column(Float(4, asdecimal=True))
    type = Column(Enum(EventType), default=EventType.undefined)
    start_ts = Column(DateTime, default=func.now())
    end_ts = Column(DateTime, default=None, nullable=True)
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    type_set_by = Column(Integer, ForeignKey("users.id"))
    type_set_ts = Column(DateTime, default=None, nullable=True)

    alerts: RelationshipProperty = relationship("Alert", back_populates="event")
    type_setter: RelationshipProperty = relationship("User", back_populates="type_set_events")

    def __repr__(self):
        return (
            f"<Event(lat='{self.lat}', lon='{self.lon}', type='{self.type}', "
            f"is_acknowledged='{self.is_acknowledged}')>"
        )
