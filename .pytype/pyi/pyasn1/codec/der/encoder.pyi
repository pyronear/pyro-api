# (generated with --quick)

import pyasn1.codec.cer.encoder
from typing import Any, List

__all__: List[str]
encode: Encoder
encoder: module
error: module
tagMap: dict
typeMap: dict
univ: module

class Encoder(pyasn1.codec.cer.encoder.Encoder):
    fixedChunkSize: int
    fixedDefLengthMode: bool

class SetEncoder(pyasn1.codec.cer.encoder.SetEncoder):
    @staticmethod
    def _componentSortKey(componentAndType) -> Any: ...
