# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import enum
from sqlalchemy import (Column, DateTime, Integer, Float, String, Table, Enum, Boolean,
                        ForeignKey, MetaData)
from sqlalchemy.sql import func


__all__ = ['metadata', 'SiteType', 'EventType', 'MediaType', 'AlertType',
           'users', 'accesses', 'sites', 'events', 'devices', 'media', 'installations', 'alerts']


# SQLAlchemy
# databases query builder
metadata = MetaData()

# Cores tables

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("login", String(50), unique=True),
    Column("access_id", Integer, ForeignKey("accesses.id"), unique=True),
    Column("created_at", DateTime, default=func.now()),
)

accesses = Table(
    "accesses",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("login", String(50), unique=True, index=True),  # index for fast lookup
    Column("hashed_password", String(70), nullable=False),
    Column("scopes", String(30), default="me", nullable=False),
)


class SiteType(str, enum.Enum):
    tower: str = 'tower'
    station: str = 'station'
    no_alert: str = 'no_alert'


sites = Table(
    "sites",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("lat", Float(4, asdecimal=True)),
    Column("lon", Float(4, asdecimal=True)),
    Column("country", String(5), nullable=False),
    Column("geocode", String(10), nullable=False),
    Column("type", Enum(SiteType), default=SiteType.tower),
    Column("created_at", DateTime, default=func.now()),
)


class EventType(str, enum.Enum):
    wildfire: str = 'wildfire'


events = Table(
    "events",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("lat", Float(4, asdecimal=True)),
    Column("lon", Float(4, asdecimal=True)),
    Column("type", Enum(EventType), default=EventType.wildfire),
    Column("start_ts", DateTime, default=None, nullable=True),
    Column("end_ts", DateTime, default=None, nullable=True),
    Column("created_at", DateTime, default=func.now()),
)


# Linked tables
devices = Table(
    "devices",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("login", String(50), unique=True),
    Column("owner_id", Integer, ForeignKey("users.id")),
    Column("access_id", Integer, ForeignKey("accesses.id"), unique=True),
    Column("specs", String(50)),
    Column("elevation", Float(1, asdecimal=True), default=None, nullable=True),
    Column("lat", Float(4, asdecimal=True), default=None, nullable=True),
    Column("lon", Float(4, asdecimal=True), default=None, nullable=True),
    Column("yaw", Float(1, asdecimal=True), default=None, nullable=True),
    Column("pitch", Float(1, asdecimal=True), default=None, nullable=True),
    Column("last_ping", DateTime, default=None, nullable=True),
    Column("created_at", DateTime, default=func.now())
)


class MediaType(str, enum.Enum):
    image: str = 'image'
    video: str = 'video'


media = Table(
    "media",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("device_id", Integer, ForeignKey("devices.id")),
    Column("bucket_key", String(100), nullable=True),
    Column("type", Enum(MediaType), default=MediaType.image),
    Column("created_at", DateTime, default=func.now()),
)


installations = Table(
    "installations",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("device_id", Integer, ForeignKey("devices.id")),
    Column("site_id", Integer, ForeignKey("sites.id")),
    Column("elevation", Float(1, asdecimal=True)),
    Column("lat", Float(4, asdecimal=True)),
    Column("lon", Float(4, asdecimal=True)),
    Column("yaw", Float(1, asdecimal=True)),
    Column("pitch", Float(1, asdecimal=True)),
    Column("start_ts", DateTime, nullable=False),
    Column("end_ts", DateTime, default=None, nullable=True),
    Column("is_trustworthy", Boolean, default=True),
    Column("created_at", DateTime, default=func.now()),
)


class AlertType(str, enum.Enum):
    start: str = 'start'
    end: str = 'end'


alerts = Table(
    "alerts",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("device_id", Integer, ForeignKey("devices.id")),
    Column("event_id", Integer, ForeignKey("events.id")),
    Column("media_id", Integer, ForeignKey("media.id"), default=None),
    Column("azimuth", Float(4, asdecimal=True), default=None),
    Column("lat", Float(4, asdecimal=True)),
    Column("lon", Float(4, asdecimal=True)),
    Column("type", Enum(AlertType), default=AlertType.start),
    Column("is_acknowledged", Boolean, default=False),
    Column("created_at", DateTime, default=func.now()),
)
