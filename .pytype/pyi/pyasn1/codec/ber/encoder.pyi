# (generated with --quick)

from typing import Any, List, NoReturn, Tuple, Type, TypeVar

LOG: int
__all__: List[str]
char: module
debug: module
encode: Encoder
eoo: module
error: module
ints2octs: Type[bytes]
null: bytes
sys: module
tag: module
tagMap: dict
typeMap: dict
univ: module
useful: module

_T0 = TypeVar('_T0')
_T1 = TypeVar('_T1')

class AbstractItemEncoder:
    eooIntegerSubstrate: Tuple[int, int]
    eooOctetsSubstrate: bytes
    supportIndefLenMode: bool
    def encode(self, value, asn1Spec = ..., encodeFun = ..., **options) -> Any: ...
    def encodeLength(self, length: _T0, defMode) -> tuple: ...
    def encodeTag(self, singleTag, isConstructed) -> tuple: ...
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> NoReturn: ...

class AnyEncoder(OctetStringEncoder):
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[Any, bool, bool]: ...

class BitStringEncoder(AbstractItemEncoder):
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[bytes, bool, bool]: ...

class BooleanEncoder(AbstractItemEncoder):
    supportIndefLenMode: bool
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[Tuple[int], bool, bool]: ...

class ChoiceEncoder(AbstractItemEncoder):
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[Any, bool, bool]: ...

class Encoder:
    _Encoder__tagMap: Any
    _Encoder__typeMap: Any
    fixedChunkSize: None
    fixedDefLengthMode: None
    def __call__(self, value, asn1Spec = ..., **options) -> Any: ...
    def __init__(self, tagMap, typeMap = ...) -> None: ...

class EndOfOctetsEncoder(AbstractItemEncoder):
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[bytes, bool, bool]: ...

class IntegerEncoder(AbstractItemEncoder):
    supportCompactZero: bool
    supportIndefLenMode: bool
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[Any, bool, bool]: ...

class NullEncoder(AbstractItemEncoder):
    supportIndefLenMode: bool
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[bytes, bool, bool]: ...

class ObjectIdentifierEncoder(AbstractItemEncoder):
    supportIndefLenMode: bool
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[tuple, bool, bool]: ...

class OctetStringEncoder(AbstractItemEncoder):
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[Any, bool, bool]: ...

class RealEncoder(AbstractItemEncoder):
    binEncBase: int
    supportIndefLenMode: int
    def _chooseEncBase(self, value) -> Any: ...
    @staticmethod
    def _dropFloatingPoint(m, encbase: _T1, e) -> Tuple[int, int, _T1, Any]: ...
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[Any, bool, bool]: ...

class SequenceEncoder(AbstractItemEncoder):
    omitEmptyOptionals: bool
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[bytes, bool, bool]: ...

class SequenceOfEncoder(AbstractItemEncoder):
    def _encodeComponents(self, value, asn1Spec, encodeFun, **options) -> list: ...
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[bytes, bool, bool]: ...

def int2oct(x) -> bytes: ...
def isOctetsType(s) -> bool: ...
def oct2int(x: _T0) -> _T0: ...
def str2octs(x) -> Any: ...
def to_bytes(value, signed = ..., length = ...) -> Any: ...
