# Copyright (C) 2020-2023, Pyronear.

# This program is licensed under the Apache License 2.0.
# See LICENSE or go to <https://opensource.org/licenses/Apache-2.0> for full license details.


from .models import Accesses, Alerts, Devices, Events, Groups, Installations, Media, Sites, Users, Webhooks
from .session import Base

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

users = Users.__table__
accesses = Accesses.__table__
groups = Groups.__table__
sites = Sites.__table__
events = Events.__table__
devices = Devices.__table__
media = Media.__table__
installations = Installations.__table__
alerts = Alerts.__table__
webhooks = Webhooks.__table__

metadata = Base.metadata
