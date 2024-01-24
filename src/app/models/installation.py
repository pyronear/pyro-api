# Copyright (C) 2021-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer
from sqlalchemy.orm import RelationshipProperty, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["Installation"]


class Installation(Base):
    __tablename__ = "installations"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    site_id = Column(Integer, ForeignKey("sites.id"))
    start_ts = Column(DateTime, nullable=False)
    end_ts = Column(DateTime, default=None, nullable=True)
    is_trustworthy = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

    device: RelationshipProperty = relationship("Device", back_populates="installation")
    site: RelationshipProperty = relationship("Site", back_populates="installations")

    def __repr__(self):
        return (
            f"<Installation(device_id='{self.device_id}', site_id='{self.site_id}', "
            f"is_trustworthy='{self.is_trustworthy}'>"
        )
