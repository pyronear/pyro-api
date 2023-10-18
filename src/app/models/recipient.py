# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

import enum

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import RelationshipProperty, relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["NotificationType", "Recipient"]


class NotificationType(str, enum.Enum):
    # email: str = "email"
    telegram: str = "telegram"


class Recipient(Base):
    __tablename__ = "recipients"

    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey("groups.id"))
    notification_type = Column(Enum(NotificationType), nullable=False)
    address = Column(String, nullable=False)
    subject_template = Column(String, nullable=False)
    message_template = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now())

    group: RelationshipProperty = relationship("Group", back_populates="recipients")
    notifications: RelationshipProperty = relationship("Notification", back_populates="recipient")

    def __repr__(self):
        return (
            f"<Recipient(group_id='{self.group_id}', notification_type='{self.notification_type}', "
            f"address='{self.address}', subject_template='{self.subject_template}', "
            f"message_template='{self.message_template}'>"
        )
