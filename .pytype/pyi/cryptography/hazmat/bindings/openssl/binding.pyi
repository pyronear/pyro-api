# (generated with --quick)

import __future__
import cryptography.exceptions
from typing import Any, Callable, Dict, Iterable, List, Sized, Tuple, Type, TypeVar

_OpenSSLErrorWithText = `namedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`

CONDITIONAL_NAMES: Dict[str, Callable[[], Any]]
InternalError: Type[cryptography.exceptions.InternalError]
absolute_import: __future__._Feature
collections: module
cryptography: module
division: __future__._Feature
ffi: Any
lib: Any
print_function: __future__._Feature
threading: module
types: module
utils: module
warnings: module

_Tnamedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text = TypeVar('_Tnamedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text', bound=`namedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`)

class Binding:
    __doc__: str
    _init_lock: threading.Lock
    _lib_loaded: bool
    _lock_init_lock: threading.Lock
    ffi: Any
    lib: module
    def __init__(self) -> None: ...
    @classmethod
    def _ensure_ffi_initialized(cls) -> None: ...
    @classmethod
    def _register_osrandom_engine(cls) -> None: ...
    @classmethod
    def init_static_locks(cls) -> None: ...

class _OpenSSLError:
    _code: Any
    _func: Any
    _lib: Any
    _reason: Any
    code: Any
    func: Any
    lib: Any
    reason: Any
    def __init__(self, code, lib, func, reason) -> None: ...
    def _lib_reason_match(self, lib, reason) -> Any: ...

class `namedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`(tuple):
    __slots__ = ["code", "func", "lib", "reason", "reason_text"]
    __dict__: collections.OrderedDict[str, Any]
    _fields: Tuple[str, str, str, str, str]
    code: Any
    func: Any
    lib: Any
    reason: Any
    reason_text: Any
    def __getnewargs__(self) -> Tuple[Any, Any, Any, Any, Any]: ...
    def __getstate__(self) -> None: ...
    def __init__(self, *args, **kwargs) -> None: ...
    def __new__(cls: Type[`_Tnamedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`], code, lib, func, reason, reason_text) -> `_Tnamedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`: ...
    def _asdict(self) -> collections.OrderedDict[str, Any]: ...
    @classmethod
    def _make(cls: Type[`_Tnamedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`], iterable: Iterable, new = ..., len: Callable[[Sized], int] = ...) -> `_Tnamedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`: ...
    def _replace(self: `_Tnamedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`, **kwds) -> `_Tnamedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`: ...

def _consume_errors(lib) -> List[_OpenSSLError]: ...
def _consume_errors_with_text(lib) -> Any: ...
def _errors_with_text(errors) -> List[`namedtuple-_OpenSSLErrorWithText-code-lib-func-reason-reason_text`]: ...
def _openssl_assert(lib, ok, errors = ...) -> None: ...
def _verify_openssl_version(lib) -> None: ...
def _verify_package_version(version) -> None: ...
def build_conditional_library(lib, conditional_names) -> module: ...
