# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["Device"]


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    access_id = Column(Integer, ForeignKey("accesses.id", ondelete="CASCADE"), unique=True)
    specs = Column(String(50))
    software_hash = Column(String(16), default=None, nullable=True)
    angle_of_view = Column(Float(2, asdecimal=True))
    elevation = Column(Float(1, asdecimal=True), default=None, nullable=True)
    lat = Column(Float(4, asdecimal=True), default=None, nullable=True)
    lon = Column(Float(4, asdecimal=True), default=None, nullable=True)
    azimuth = Column(Float(1, asdecimal=True), default=None, nullable=True)
    pitch = Column(Float(1, asdecimal=True), default=None, nullable=True)
    last_ping = Column(DateTime, default=None, nullable=True)
    created_at = Column(DateTime, default=func.now())

    access = relationship("Access", uselist=False, back_populates="device")
    owner = relationship("User", uselist=False, back_populates="device")
    media = relationship("Media", back_populates="device")
    alerts = relationship("Alert", back_populates="device")
    installation = relationship("Installation", back_populates="device")

    def __repr__(self):
        return (
            f"<Device(login='{self.login}', owner_id='{self.owner_id}', access_id='{self.access_id}', "
            f"specs='{self.specs}', software_hash='{self.software_hash}', last_ping='{self.last_ping}')>"
        )
