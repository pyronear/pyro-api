# (generated with --quick)

import __future__
import typing
from typing import Any, Callable, Dict, Generator, Iterable, List, Mapping, NoReturn, Optional, Sequence, Set, Tuple, Type, TypeVar, Union

BytesIO: Type[io.BytesIO]
Iterator: type
MAXSIZE: int
PY2: bool
PY3: bool
PY34: bool
StringIO: Type[io.StringIO]
__author__: str
__package__: Optional[str]
__path__: List[nothing]
__version__: str
_assertCountEqual: str
_assertRaisesRegex: str
_assertRegex: str
_func_closure: str
_func_code: str
_func_defaults: str
_func_globals: str
_importer: _SixMetaPathImporter
_meth_func: str
_meth_self: str
_moved_attributes: list
_urllib_error_moved_attributes: List[MovedAttribute]
_urllib_parse_moved_attributes: List[MovedAttribute]
_urllib_request_moved_attributes: List[MovedAttribute]
_urllib_response_moved_attributes: List[MovedAttribute]
_urllib_robotparser_moved_attributes: List[MovedAttribute]
absolute_import: __future__._Feature
attr: Any
binary_type: Type[bytes]
byte2int: Callable[[Any], Any]
class_types: Tuple[Type[type]]
create_bound_method: Type[types.MethodType]
exec_: Any
functools: module
get_function_closure: Callable[[Any], Any]
get_function_code: Callable[[Any], Any]
get_function_defaults: Callable[[Any], Any]
get_function_globals: Callable[[Any], Any]
get_method_function: Callable[[Any], Any]
get_method_self: Callable[[Any], Any]
i: Any
importer: Any
integer_types: Tuple[Type[int]]
io: Any
itertools: module
moves: _MovedItems
operator: module
print_: Any
string_types: Tuple[Type[str]]
struct: Any
sys: module
text_type: Type[str]
types: module
viewitems: Callable
viewkeys: Callable
viewvalues: Callable

_K = TypeVar('_K')
_T = TypeVar('_T')
_T0 = TypeVar('_T0')
_T2 = TypeVar('_T2')
_V = TypeVar('_V')

class Module_six_moves_urllib(module):
    __doc__: str
    __path__: List[nothing]
    error: Any
    parse: Any
    request: Any
    response: Any
    robotparser: Any
    def __dir__(self) -> List[str]: ...

class Module_six_moves_urllib_error(_LazyModule):
    __doc__: Any
    _moved_attributes: List[MovedAttribute]

class Module_six_moves_urllib_parse(_LazyModule):
    __doc__: Any
    _moved_attributes: List[MovedAttribute]

class Module_six_moves_urllib_request(_LazyModule):
    __doc__: Any
    _moved_attributes: List[MovedAttribute]

class Module_six_moves_urllib_response(_LazyModule):
    __doc__: Any
    _moved_attributes: List[MovedAttribute]

class Module_six_moves_urllib_robotparser(_LazyModule):
    __doc__: Any
    _moved_attributes: List[MovedAttribute]

class MovedAttribute(_LazyDescr):
    attr: Any
    mod: Any
    name: Any
    def __init__(self, name, old_mod, new_mod, old_attr = ..., new_attr = ...) -> None: ...
    def _resolve(self) -> Any: ...

class MovedModule(_LazyDescr):
    mod: Any
    name: Any
    def __getattr__(self, attr) -> Any: ...
    def __init__(self, name, old, new = ...) -> None: ...
    def _resolve(self) -> Any: ...

class _LazyDescr:
    name: Any
    def __get__(self, obj, tp) -> Any: ...
    def __init__(self, name) -> None: ...

class _LazyModule(module):
    __doc__: Any
    _moved_attributes: List[nothing]
    def __dir__(self) -> list: ...
    def __init__(self, name) -> None: ...

class _MovedItems(_LazyModule):
    __doc__: Any
    __path__: List[nothing]
    _moved_attributes: list

class _SixMetaPathImporter:
    __doc__: str
    known_modules: dict
    name: Any
    def _SixMetaPathImporter__get_module(self, fullname) -> Any: ...
    def __init__(self, six_module_name) -> None: ...
    def _add_module(self, mod, *fullnames) -> None: ...
    def _get_module(self, fullname) -> Any: ...
    def find_module(self, fullname, path = ...) -> Optional[_SixMetaPathImporter]: ...
    def get_code(self, fullname) -> None: ...
    def get_source(self, fullname) -> None: ...
    def is_package(self, fullname) -> bool: ...
    def load_module(self, fullname) -> Any: ...

def _add_doc(func, doc) -> None: ...
def _import_module(name) -> Any: ...
def add_metaclass(metaclass) -> Callable[[Any], Any]: ...
def add_move(move) -> None: ...
@overload
def advance_iterator(it) -> Any: ...
@overload
def advance_iterator(iterator: typing.Iterator[_T], default: _T2 = ...) -> Union[_T, _T2]: ...
def assertCountEqual(self, *args, **kwargs) -> Any: ...
def assertRaisesRegex(self, *args, **kwargs) -> Any: ...
def assertRegex(self, *args, **kwargs) -> Any: ...
def b(s) -> Any: ...
def callable(obj) -> bool: ...
def create_unbound_method(func: _T0, cls) -> _T0: ...
def ensure_binary(s, encoding = ..., errors = ...) -> Any: ...
def ensure_str(s, encoding = ..., errors = ...) -> Any: ...
def ensure_text(s, encoding = ..., errors = ...) -> Any: ...
def get_unbound_function(unbound: _T0) -> _T0: ...
@overload
def indexbytes(__a: Mapping[_K, _V], __b: _K) -> _V: ...
@overload
def indexbytes(__a: Sequence[_T], __b: int) -> _T: ...
def int2byte(*v) -> bytes: ...
@overload
def iterbytes(collection: bytearray) -> bytearray_iterator: ...
@overload
def iterbytes(collection: Dict[_T, _T2]) -> typing.Iterator[_T]: ...
@overload
def iterbytes(collection: Generator[_T]) -> Generator[_T]: ...
@overload
def iterbytes(collection: List[_T]) -> listiterator[_T]: ...
@overload
def iterbytes(collection: Set[_T]) -> setiterator[_T]: ...
@overload
def iterbytes(collection: Tuple[_T, ...]) -> tupleiterator[_T]: ...
@overload
def iterbytes(collection: Iterable[_T]) -> typing.Iterator[_T]: ...
@overload
def iterbytes(func: Callable[[], Union[_T, _T2]], sentinel: _T) -> typing.Iterator[_T2]: ...
def iteritems(d, **kw) -> Any: ...
def iterkeys(d, **kw) -> Any: ...
def iterlists(d, **kw) -> Any: ...
def itervalues(d, **kw) -> Any: ...
@overload
def next(it) -> Any: ...
@overload
def next(iterator: typing.Iterator[_T], default: _T2 = ...) -> Union[_T, _T2]: ...
def python_2_unicode_compatible(klass: _T0) -> _T0: ...
def remove_move(name) -> None: ...
def reraise(tp, value, tb = ...) -> NoReturn: ...
def u(s: _T0) -> _T0: ...
def unichr(i: int) -> str: ...
def with_metaclass(meta, *bases) -> type: ...
def wraps(wrapped: Callable, assigned: Sequence[str] = ..., updated: Sequence[str] = ...) -> Callable[[Callable], Callable]: ...
