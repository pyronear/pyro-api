# (generated with --quick)

import pyasn1.type.base
import pyasn1.type.tag
from typing import List, Type, TypeVar

__all__: List[str]
base: module
endOfOctets: EndOfOctets
tag: module

_TEndOfOctets = TypeVar('_TEndOfOctets', bound=EndOfOctets)

class EndOfOctets(pyasn1.type.base.SimpleAsn1Type):
    _instance: EndOfOctets
    defaultValue: int
    tagSet: pyasn1.type.tag.TagSet
    def __new__(cls: Type[_TEndOfOctets], *args, **kwargs) -> _TEndOfOctets: ...
