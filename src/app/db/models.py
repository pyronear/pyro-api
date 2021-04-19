# Copyright (C) 2021, Pyronear contributors.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

import enum
from .session import Base
from sqlalchemy.sql import func
from sqlalchemy import Column, DateTime, Integer, Float, String, Enum, Boolean, ForeignKey, MetaData


class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    access_id = Column(Integer, ForeignKey("accesses.id", ondelete="CASCADE"), unique=True)
    created_at = Column(DateTime, default=func.now())


class AccessType(str, enum.Enum):
    user: str = 'user'
    admin: str = 'admin'
    device: str = 'device'


class Accesses(Base):
    __tablename__ = "accesses"

    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True, index=True)  # index for fast lookup
    hashed_password = Column(String(70), nullable=False)
    scope = Column(Enum(AccessType), default=AccessType.user, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)


class Groups(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)


class SiteType(str, enum.Enum):
    tower: str = 'tower'
    station: str = 'station'
    no_alert: str = 'no_alert'


class Sites(Base):
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    group_id = Column(Integer, ForeignKey("groups.id", ondelete="CASCADE"), nullable=False)
    lat = Column(Float(4, asdecimal=True))
    lon = Column(Float(4, asdecimal=True))
    country = Column(String(5), nullable=False)
    geocode = Column(String(10), nullable=False)
    type = Column(Enum(SiteType), default=SiteType.tower)
    created_at = Column(DateTime, default=func.now())


class EventType(str, enum.Enum):
    wildfire: str = 'wildfire'


class Events(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True)
    lat = Column(Float(4, asdecimal=True))
    lon = Column(Float(4, asdecimal=True))
    type = Column(Enum(EventType), default=EventType.wildfire)
    start_ts = Column(DateTime, default=None, nullable=True)
    end_ts = Column(DateTime, default=None, nullable=True)
    created_at = Column(DateTime, default=func.now())


# Linked tables
class Devices(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True)
    login = Column(String(50), unique=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    access_id = Column(Integer, ForeignKey("accesses.id", ondelete="CASCADE"), unique=True)
    specs = Column(String(50))
    software_hash = Column(String(16), default=None, nullable=True)
    angle_of_view = Column(Float(2, asdecimal=True))
    elevation = Column(Float(1, asdecimal=True), default=None, nullable=True)
    lat = Column(Float(4, asdecimal=True), default=None, nullable=True)
    lon = Column(Float(4, asdecimal=True), default=None, nullable=True)
    yaw = Column(Float(1, asdecimal=True), default=None, nullable=True)
    pitch = Column(Float(1, asdecimal=True), default=None, nullable=True)
    last_ping = Column(DateTime, default=None, nullable=True)
    created_at = Column(DateTime, default=func.now())


class MediaType(str, enum.Enum):
    image: str = 'image'
    video: str = 'video'


class Media(Base):
    __tablename__ = "media"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    bucket_key = Column(String(100), nullable=True)
    type = Column(Enum(MediaType), default=MediaType.image)
    created_at = Column(DateTime, default=func.now())


class Installations(Base):
    __tablename__ = "installations"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    site_id = Column(Integer, ForeignKey("sites.id"))
    start_ts = Column(DateTime, nullable=False)
    end_ts = Column(DateTime, default=None, nullable=True)
    is_trustworthy = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())


class Alerts(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True)
    device_id = Column(Integer, ForeignKey("devices.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    media_id = Column(Integer, ForeignKey("media.id"), default=None)
    azimuth = Column(Float(4, asdecimal=True), default=None)
    lat = Column(Float(4, asdecimal=True))
    lon = Column(Float(4, asdecimal=True))
    is_acknowledged = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())


class Webhooks(Base):
    __tablename__ = "webhooks"

    id = Column(Integer, primary_key=True)
    callback = Column(String(50), nullable=False)
    url = Column(String(100), nullable=False)
