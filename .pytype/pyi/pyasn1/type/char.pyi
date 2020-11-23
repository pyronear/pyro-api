# (generated with --quick)

import pyasn1.type.base
import pyasn1.type.univ
from typing import Any, List, Tuple, Type, TypeVar

NoValue: Type[pyasn1.type.base.NoValue]
__all__: List[str]
error: module
noValue: pyasn1.type.base.NoValue
sys: module
tag: module
univ: module

_T0 = TypeVar('_T0')

class AbstractCharacterString(pyasn1.type.univ.OctetString):
    __doc__: str
    def __bytes__(self) -> Any: ...
    def __reversed__(self) -> reversed: ...
    def __str__(self) -> str: ...
    def asNumbers(self, padding = ...) -> Tuple[int, ...]: ...
    def asOctets(self, padding = ...) -> bytes: ...
    def prettyIn(self, value) -> Any: ...
    def prettyOut(self, value: _T0) -> _T0: ...
    def prettyPrint(self, scope = ...) -> Any: ...

class BMPString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class GeneralString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class GraphicString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class IA5String(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class ISO646String(VisibleString):
    __doc__: str
    typeId: Any

class NumericString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class PrintableString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class T61String(TeletexString):
    __doc__: str
    typeId: Any

class TeletexString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class UTF8String(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class UniversalString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class VideotexString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any

class VisibleString(AbstractCharacterString):
    __doc__: str
    encoding: str
    tagSet: Any
    typeId: Any
