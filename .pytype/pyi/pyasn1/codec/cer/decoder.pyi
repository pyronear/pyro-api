# (generated with --quick)

import pyasn1.codec.ber.decoder
import pyasn1.type.univ
from typing import Any, List, Tuple, Type, TypeVar

BitStringDecoder: Type[pyasn1.codec.ber.decoder.BitStringDecoder]
OctetStringDecoder: Type[pyasn1.codec.ber.decoder.OctetStringDecoder]
RealDecoder: Type[pyasn1.codec.ber.decoder.RealDecoder]
__all__: List[str]
decode: Decoder
decoder: module
error: module
tagMap: dict
typeDecoder: Any
typeId: Any
typeMap: dict
univ: module

_T0 = TypeVar('_T0')

class BooleanDecoder(pyasn1.codec.ber.decoder.AbstractSimpleDecoder):
    protoComponent: pyasn1.type.univ.Boolean
    def valueDecoder(self, substrate, asn1Spec, tagSet = ..., length = ..., state = ..., decodeFun = ..., substrateFun = ..., **options) -> Tuple[Any, Any]: ...

class Decoder(pyasn1.codec.ber.decoder.Decoder): ...

def oct2int(x: _T0) -> _T0: ...
