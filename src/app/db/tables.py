# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from app.models import Access, Alert, Device, Event, Group, Installation, Media, Site, User, Webhook

from .base_class import Base

__all__ = [
    "metadata",
    "users",
    "accesses",
    "groups",
    "sites",
    "events",
    "devices",
    "media",
    "installations",
    "alerts",
    "webhooks",
]

users = User.__table__
accesses = Access.__table__
groups = Group.__table__
sites = Site.__table__
events = Event.__table__
devices = Device.__table__
media = Media.__table__
installations = Installation.__table__
alerts = Alert.__table__
webhooks = Webhook.__table__

metadata = Base.metadata
