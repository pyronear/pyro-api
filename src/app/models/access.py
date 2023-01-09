# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import enum

from sqlalchemy import Column, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.base_class import Base

__all__ = ["AccessType", "Access"]


class AccessType(str, enum.Enum):
    user: str = "user"
    admin: str = "admin"
    device: str = "device"


class Access(Base):
    __tablename__ = "accesses"

    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True, index=True)  # index for fast lookup
    hashed_password = Column(String(70), nullable=False)
    scope = Column(Enum(AccessType), default=AccessType.user, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)

    user = relationship("Users", uselist=False, back_populates="access")
    device = relationship("Devices", uselist=False, back_populates="access")
    group = relationship("Groups", uselist=False, back_populates="accesses")

    def __repr__(self):
        return f"<Access(login='{self.login}', scope='{self.scope}', group_id='{self.group_id}')>"
