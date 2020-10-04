import os
import enum
from sqlalchemy import (Column, DateTime, Integer, Float, String, Table, Enum, Boolean,
                        ForeignKey, MetaData, create_engine)
from sqlalchemy.sql import func
from app import config as cfg
from databases import Database


# SQLAlchemy
# databases query builder
database = Database(cfg.DATABASE_URL)
engine = create_engine(cfg.DATABASE_URL)
metadata = MetaData()

# Cores tables

users = Table(
    "users",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("username", String(50)),
    Column("created_at", DateTime, default=func.now()),
)


class SiteType(str, enum.Enum):
    tower: str = 'tower'
    station: str = 'station'


sites = Table(
    "sites",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("lat", Float(4, asdecimal=True)),
    Column("lon", Float(4, asdecimal=True)),
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
    Column("name", String(50)),
    Column("owner_id", Integer, ForeignKey("users.id")),
    Column("specs", String(50)),
    Column("last_elevation", Float(1, asdecimal=True), default=None, nullable=True),
    Column("last_lat", Float(4, asdecimal=True), default=None, nullable=True),
    Column("last_lon", Float(4, asdecimal=True), default=None, nullable=True),
    Column("last_yaw", Float(1, asdecimal=True), default=None, nullable=True),
    Column("last_pitch", Float(1, asdecimal=True), default=None, nullable=True),
    Column("last_ping", DateTime, default=None, nullable=True),
    Column("created_at", DateTime, default=func.now()),
)


class MediaType(str, enum.Enum):
    image: str = 'image'
    video: str = 'video'


media = Table(
    "media",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("device_id", Integer, ForeignKey("devices.id")),
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
    Column("start_ts", DateTime, default=None, nullable=True),
    Column("end_ts", DateTime, default=None, nullable=True),
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
    Column("lat", Float(4, asdecimal=True)),
    Column("lon", Float(4, asdecimal=True)),
    Column("type", Enum(AlertType), default=AlertType.start),
    Column("is_acknowledged", Boolean, default=False),
    Column("created_at", DateTime, default=func.now()),
)
