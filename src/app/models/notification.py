# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base_class import Base

__all__ = ["Notification"]


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    alert_id = Column(Integer, ForeignKey("alerts.id"))
    recipient_id = Column(Integer, ForeignKey("recipients.id"))
    message = Column(String, nullable=False)

    alert = relationship("Alert", uselist=False, back_populates="notifications")
    recipient = relationship("Recipient", uselist=False, back_populates="notifications")

    def __repr__(self):
        return (
            f"<Notification(alert_id='{self.alert_id}', recipient_id='{self.recipient_id}', "
            f"message='{self.message}'>"
        )
