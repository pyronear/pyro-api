# (generated with --quick)

from typing import Any

Boolean: Any
Column: Any
Database: Any
DateTime: Any
Enum: Any
Float: Any
ForeignKey: Any
Integer: Any
MetaData: Any
String: Any
Table: Any
alerts: Any
cfg: module
create_engine: Any
database: Any
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
