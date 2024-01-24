# Copyright (C) 2021-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import enum

from sqlalchemy import Column, DateTime, Enum, Float, ForeignKey, Integer, String
from sqlalchemy.orm import RelationshipProperty, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["SiteType", "Site"]


class SiteType(str, enum.Enum):
    tower: str = "tower"
    station: str = "station"
    no_alert: str = "no_alert"


class Site(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    lat = Column(Float(4, asdecimal=True))
    lon = Column(Float(4, asdecimal=True))
    country = Column(String(5), nullable=False)
    geocode = Column(String(10), nullable=False)
    type = Column(Enum(SiteType), default=SiteType.tower)
    created_at = Column(DateTime, default=func.now())

    installations: RelationshipProperty = relationship("Installation", back_populates="site")
    group: RelationshipProperty = relationship("Group", uselist=False, back_populates="sites")

    def __repr__(self):
        return (
            f"<Site(name='{self.name}', group_id='{self.group_id}', lat='{self.lat}', lon='{self.lon}', "
            f"country='{self.country}', geocode='{self.geocode}', type='{self.type}')>"
        )
