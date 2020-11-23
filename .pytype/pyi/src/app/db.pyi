# (generated with --quick)

import databases.core
from typing import Any, Type

Boolean: Any
Column: Any
Database: Type[databases.core.Database]
DateTime: Any
Enum: Any
Float: Any
ForeignKey: Any
Integer: Any
MetaData: Any
String: Any
Table: Any
accesses: Any
alerts: Any
cfg: module
database: databases.core.Database
devices: Any
engine: Any
enum: module
events: Any
func: Any
installations: Any
media: Any
metadata: Any
sites: Any
users: Any

class AlertType(str, enum.Enum):
    end: str
    start: str

class EventType(str, enum.Enum):
    wildfire: str

class MediaType(str, enum.Enum):
    image: str
    video: str

class SiteType(str, enum.Enum):
    station: str
    tower: str

def create_engine(*args, **kwargs) -> Any: ...
