# (generated with --quick)

import pyasn1.type.base
import pyasn1.type.char
from typing import Any, List, Type, TypeVar

NoValue: Type[pyasn1.type.base.NoValue]
__all__: List[str]
char: module
dateandtime: module
datetime: module
error: module
noValue: pyasn1.type.base.NoValue
string: module
tag: module
univ: module

_TTimeMixIn = TypeVar('_TTimeMixIn', bound=TimeMixIn)

class GeneralizedTime(pyasn1.type.char.VisibleString, TimeMixIn):
    __doc__: str
    _hasSubsecond: bool
    _optionalMinutes: bool
    _shortTZ: bool
    _yearsDigits: int
    tagSet: Any
    typeId: Any

class ObjectDescriptor(pyasn1.type.char.GraphicString):
    __doc__: str
    tagSet: Any
    typeId: Any

class TimeMixIn:
    FixedOffset: type
    UTC: Any
    _hasSubsecond: bool
    _optionalMinutes: bool
    _shortTZ: bool
    _yearsDigits: int
    asDateTime: datetime.datetime
    @classmethod
    def fromDateTime(cls: Type[_TTimeMixIn], dt) -> _TTimeMixIn: ...

class UTCTime(pyasn1.type.char.VisibleString, TimeMixIn):
    __doc__: str
    _hasSubsecond: bool
    _optionalMinutes: bool
    _shortTZ: bool
    _yearsDigits: int
    tagSet: Any
    typeId: Any
