# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import RelationshipProperty, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["User"]


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    access_id = Column(Integer, ForeignKey("accesses.id", ondelete="CASCADE"), unique=True)
    created_at = Column(DateTime, default=func.now())

    access: RelationshipProperty = relationship("Access", uselist=False, back_populates="user")
    device: RelationshipProperty = relationship("Device", uselist=False, back_populates="owner")

    def __repr__(self):
        return f"<User(login='{self.login}', created_at='{self.created_at}'>"
