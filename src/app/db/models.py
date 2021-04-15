# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

from .tables import users, accesses, groups, sites, events, devices, media, installations, alerts, webhooks
from .session import Base


class Users(Base):
    __table__ = users


class Accesses(Base):
    __table__ = accesses


class Groups(Base):
    __table__ = groups


class Sites(Base):
    __table__ = sites


class Events(Base):
    __table__ = events


class Devices(Base):
    __table__ = devices


class Media(Base):
    __table__ = media


class Installations(Base):
    __table__ = installations


class Alerts(Base):
    __table__ = alerts


class Webhooks(Base):
    __table__ = webhooks
