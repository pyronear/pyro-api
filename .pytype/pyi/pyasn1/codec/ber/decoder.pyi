# (generated with --quick)

import pyasn1.type.base
import pyasn1.type.char
import pyasn1.type.tag
import pyasn1.type.univ
import pyasn1.type.useful
from typing import Any, Dict, List, NoReturn, Tuple, Type, TypeVar

LOG: int
__all__: List[str]
base: module
char: module
debug: module
decode: Decoder
eoo: module
error: module
explicitTagDecoder: ExplicitTagDecoder
ints2octs: Type[bytes]
noValue: pyasn1.type.base.NoValue
null: bytes
stDecodeLength: int
stDecodeTag: int
stDecodeValue: int
stDumpRawValue: int
stErrorCondition: int
stGetValueDecoder: int
stGetValueDecoderByAsn1Spec: int
stGetValueDecoderByTag: int
stStop: int
stTryAsExplicitTag: int
tag: module
tagMap: dict
tagmap: module
typeDecoder: Any
typeId: Any
typeMap: dict
univ: module
useful: module

_T0 = TypeVar('_T0')

class AbstractConstructedDecoder(AbstractDecoder):
    protoComponent: None

class AbstractDecoder:
    protoComponent: None
    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> NoReturn: ...
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> NoReturn: ...

class AbstractSimpleDecoder(AbstractDecoder):
    def _createComponent(self, asn1Spec, tagSet, value, **options) -> Any: ...
    @staticmethod
    def substrateCollector(asn1Object, substrate, length) -> Tuple[Any, Any]: ...

class AnyDecoder(AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.Any
    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...

class BMPStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.BMPString

class BitStringDecoder(AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.BitString
    supportConstructedForm: bool
    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...

class BooleanDecoder(IntegerDecoder):
    protoComponent: pyasn1.type.univ.Boolean
    def _createComponent(self, asn1Spec, tagSet, value, **options) -> Any: ...

class ChoiceDecoder(AbstractConstructedDecoder):
    protoComponent: pyasn1.type.univ.Choice
    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...

class Decoder:
    _Decoder__eooSentinel: bytes
    _Decoder__tagCache: Dict[Any, pyasn1.type.tag.Tag]
    _Decoder__tagMap: Any
    _Decoder__tagSetCache: Dict[Any, pyasn1.type.tag.TagSet]
    _Decoder__typeMap: Any
    defaultErrorState: int
    defaultRawDecoder: AnyDecoder
    supportIndefLength: bool
    def __call__(self, substrate, asn1Spec = ..., tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Tuple[Any, Any]: ...
    def __init__(self, tagMap, typeMap = ...) -> None: ...

class ExplicitTagDecoder(AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.Any
    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...

class GeneralStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.GeneralString

class GeneralizedTimeDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.useful.GeneralizedTime

class GraphicStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.GraphicString

class IA5StringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.IA5String

class IntegerDecoder(AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.Integer
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Tuple[Any, Any]: ...

class NullDecoder(AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.Null
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Tuple[Any, Any]: ...

class NumericStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.NumericString

class ObjectDescriptorDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.useful.ObjectDescriptor

class ObjectIdentifierDecoder(AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.ObjectIdentifier
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Tuple[Any, Any]: ...

class OctetStringDecoder(AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.OctetString
    supportConstructedForm: bool
    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...

class PrintableStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.PrintableString

class RealDecoder(AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.Real
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Tuple[Any, Any]: ...

class SequenceDecoder(SequenceOrSequenceOfDecoder):
    protoComponent: pyasn1.type.univ.Sequence

class SequenceOfDecoder(SequenceOrSequenceOfDecoder):
    protoComponent: pyasn1.type.univ.SequenceOf

class SequenceOrSequenceOfDecoder(UniversalConstructedTypeDecoder):
    protoRecordComponent: pyasn1.type.univ.Sequence
    protoSequenceComponent: pyasn1.type.univ.SequenceOf

class SetDecoder(SetOrSetOfDecoder):
    protoComponent: pyasn1.type.univ.Set

class SetOfDecoder(SetOrSetOfDecoder):
    protoComponent: pyasn1.type.univ.SetOf

class SetOrSetOfDecoder(UniversalConstructedTypeDecoder):
    protoRecordComponent: pyasn1.type.univ.Set
    protoSequenceComponent: pyasn1.type.univ.SetOf

class TeletexStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.TeletexString

class UTCTimeDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.useful.UTCTime

class UTF8StringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.UTF8String

class UniversalConstructedTypeDecoder(AbstractConstructedDecoder):
    protoRecordComponent: None
    protoSequenceComponent: None
    def _decodeComponents(self, substrate, tagSet = ..., decodeFun = ..., **options) -> Tuple[Any, Any]: ...
    def _getComponentPositionByType(self, asn1Object, tagSet, idx) -> NoReturn: ...
    def _getComponentTagMap(self, asn1Object, idx) -> NoReturn: ...
    def indefLenValueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Any: ...

class UniversalStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.UniversalString

class VideotexStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.VideotexString

class VisibleStringDecoder(OctetStringDecoder):
    protoComponent: pyasn1.type.char.VisibleString

def from_bytes(octets, signed = ...) -> int: ...
def oct2int(x: _T0) -> _T0: ...
def octs2ints(x: _T0) -> _T0: ...
