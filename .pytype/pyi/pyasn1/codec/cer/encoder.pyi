# (generated with --quick)

import pyasn1.codec.ber.encoder
from typing import Any, List, Tuple

__all__: List[str]
encode: Encoder
encoder: module
error: module
null: bytes
tagMap: dict
typeMap: dict
univ: module
useful: module

class BooleanEncoder(pyasn1.codec.ber.encoder.IntegerEncoder):
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[Tuple[int], bool, bool]: ...

class Encoder(pyasn1.codec.ber.encoder.Encoder):
    fixedChunkSize: int
    fixedDefLengthMode: bool

class GeneralizedTimeEncoder(TimeEncoderMixIn, pyasn1.codec.ber.encoder.OctetStringEncoder):
    MAX_LENGTH: int
    MIN_LENGTH: int

class RealEncoder(pyasn1.codec.ber.encoder.RealEncoder):
    def _chooseEncBase(self, value) -> Tuple[int, int, Any, Any]: ...

class SequenceEncoder(pyasn1.codec.ber.encoder.SequenceEncoder):
    omitEmptyOptionals: bool

class SequenceOfEncoder(pyasn1.codec.ber.encoder.SequenceOfEncoder):
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[bytes, bool, bool]: ...

class SetEncoder(pyasn1.codec.ber.encoder.SequenceEncoder):
    @staticmethod
    def _componentSortKey(componentAndType) -> Any: ...
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[bytes, bool, bool]: ...

class SetOfEncoder(pyasn1.codec.ber.encoder.SequenceOfEncoder):
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Tuple[bytes, bool, bool]: ...

class TimeEncoderMixIn:
    COMMA_CHAR: int
    DOT_CHAR: int
    MAX_LENGTH: int
    MINUS_CHAR: int
    MIN_LENGTH: int
    PLUS_CHAR: int
    ZERO_CHAR: int
    Z_CHAR: int
    def encodeValue(self, value, asn1Spec, encodeFun, **options) -> Any: ...

class UTCTimeEncoder(TimeEncoderMixIn, pyasn1.codec.ber.encoder.OctetStringEncoder):
    MAX_LENGTH: int
    MIN_LENGTH: int

def str2octs(x) -> Any: ...
