# (generated with --quick)

import __future__
import packaging._structures
from typing import Any, Callable, Dict, Iterable, Iterator, List, Optional, Pattern, Sized, Tuple, Type, TypeVar, Union

CmpKey = Tuple[int, Tuple[int, ...], Union[packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[str, int]], Union[packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[str, int]], Union[packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[str, int]], Union[packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]]]
LegacyCmpKey = Tuple[int, Tuple[str, ...]]
VersionComparisonMethod = Callable[[Tuple[Union[int, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]], ...], Tuple[Union[int, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]], ...]], bool]
_Version = `namedtuple-_Version-epoch-release-dev-pre-post-local`

InfiniteTypes: Type[Union[packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]
Infinity: packaging._structures.InfinityType
InfinityType: Type[packaging._structures.InfinityType]
LocalType: Type[Union[packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]]]
NegativeInfinity: packaging._structures.NegativeInfinityType
NegativeInfinityType: Type[packaging._structures.NegativeInfinityType]
PrePostDevType: Type[Union[packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[str, int]]]
SubLocalType: Type[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]
TYPE_CHECKING: bool
VERSION_PATTERN: str
__all__: List[str]
_legacy_version_component_re: Pattern[str]
_legacy_version_replacement_map: Dict[str, str]
_local_version_separators: Pattern[str]
absolute_import: __future__._Feature
collections: module
division: __future__._Feature
itertools: module
print_function: __future__._Feature
re: module

_Tnamedtuple-_Version-epoch-release-dev-pre-post-local = TypeVar('_Tnamedtuple-_Version-epoch-release-dev-pre-post-local', bound=`namedtuple-_Version-epoch-release-dev-pre-post-local`)

class InvalidVersion(ValueError):
    __doc__: str

class LegacyVersion(_BaseVersion):
    _key: Any
    _version: str
    base_version: str
    dev: None
    epoch: int
    is_devrelease: bool
    is_postrelease: bool
    is_prerelease: bool
    local: None
    post: None
    pre: None
    public: str
    release: None
    def __init__(self, version: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class Version(_BaseVersion):
    _key: Any
    _regex: Pattern[str]
    _version: `namedtuple-_Version-epoch-release-dev-pre-post-local`
    base_version: str
    dev: Optional[Tuple[str, int]]
    epoch: int
    is_devrelease: bool
    is_postrelease: bool
    is_prerelease: bool
    local: Optional[str]
    major: int
    micro: int
    minor: int
    post: Optional[Tuple[str, int]]
    pre: Optional[Tuple[str, int]]
    public: str
    release: Tuple[int, ...]
    def __init__(self, version: str) -> None: ...
    def __repr__(self) -> str: ...
    def __str__(self) -> str: ...

class _BaseVersion:
    _key: Tuple[Union[int, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]], ...]
    def __eq__(self, other: object) -> bool: ...
    def __ge__(self, other: _BaseVersion) -> bool: ...
    def __gt__(self, other: _BaseVersion) -> bool: ...
    def __hash__(self) -> int: ...
    def __le__(self, other: _BaseVersion) -> bool: ...
    def __lt__(self, other: _BaseVersion) -> bool: ...
    def __ne__(self, other: object) -> bool: ...
    def _compare(self, other: object, method: Callable[[Tuple[Union[int, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]], ...], Tuple[Union[int, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]], ...]], bool]) -> Any: ...

class `namedtuple-_Version-epoch-release-dev-pre-post-local`(tuple):
    __slots__ = ["dev", "epoch", "local", "post", "pre", "release"]
    __dict__: collections.OrderedDict[str, Any]
    _fields: Tuple[str, str, str, str, str, str]
    dev: Any
    epoch: Any
    local: Any
    post: Any
    pre: Any
    release: Any
    def __getnewargs__(self) -> Tuple[Any, Any, Any, Any, Any, Any]: ...
    def __getstate__(self) -> None: ...
    def __init__(self, *args, **kwargs) -> None: ...
    def __new__(cls: Type[`_Tnamedtuple-_Version-epoch-release-dev-pre-post-local`], epoch, release, dev, pre, post, local) -> `_Tnamedtuple-_Version-epoch-release-dev-pre-post-local`: ...
    def _asdict(self) -> collections.OrderedDict[str, Any]: ...
    @classmethod
    def _make(cls: Type[`_Tnamedtuple-_Version-epoch-release-dev-pre-post-local`], iterable: Iterable, new = ..., len: Callable[[Sized], int] = ...) -> `_Tnamedtuple-_Version-epoch-release-dev-pre-post-local`: ...
    def _replace(self: `_Tnamedtuple-_Version-epoch-release-dev-pre-post-local`, **kwds) -> `_Tnamedtuple-_Version-epoch-release-dev-pre-post-local`: ...

def _cmpkey(epoch, release, pre, post, dev, local) -> Tuple[int, Tuple[int, ...], Union[packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[str, int]], Union[packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[str, int]], Union[packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[str, int]], Union[packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]]]: ...
def _legacy_cmpkey(version: str) -> Tuple[int, Tuple[str, ...]]: ...
def _parse_letter_version(letter, number) -> Optional[Tuple[str, int]]: ...
def _parse_local_version(local: str) -> Optional[Union[packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType, Tuple[Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType], Union[int, str, packaging._structures.InfinityType, packaging._structures.NegativeInfinityType]]], ...]]]: ...
def _parse_version_parts(s: str) -> Iterator[str]: ...
def parse(version: str) -> Union[LegacyVersion, Version]: ...
