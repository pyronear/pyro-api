# (generated with --quick)

import datetime
from typing import Any, Type

timedelta: Type[datetime.timedelta]
tzinfo: Type[datetime.tzinfo]

class TomlTz(datetime.tzinfo):
    _hours: int
    _minutes: int
    _raw_offset: Any
    _sign: int
    def __init__(self, toml_offset) -> None: ...
    def dst(self, dt) -> datetime.timedelta: ...
    def tzname(self, dt) -> str: ...
    def utcoffset(self, dt) -> datetime.timedelta: ...
