# Copyright (C) 2021-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from sqlalchemy import Column, Integer, String

from app.db.base_class import Base

__all__ = ["Webhook"]


class Webhook(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True)
    callback = Column(String(50), nullable=False)
    url = Column(String(100), nullable=False)

    def __repr__(self):
        return f"<Webhook(callback='{self.callback}', url='{self.url}'>"
