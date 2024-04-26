# Copyright (C) 2021-2024, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import RelationshipProperty, relationship

from app.db.base_class import Base

__all__ = ["Group"]


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)

    accesses: RelationshipProperty = relationship("Access", back_populates="group")
    sites: RelationshipProperty = relationship("Site", back_populates="group")
    recipients: RelationshipProperty = relationship("Recipient", back_populates="group")

    def __repr__(self):
        return f"<Group(name='{self.name}')>"
