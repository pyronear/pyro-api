# (generated with --quick)

import click._compat
from typing import Any, Callable, Dict, List, Optional, Tuple, Type, TypeVar, Union

c_ssize_p = ctypes.pointer[_CT]

CommandLineToArgvW: Any
DWORD: Type[ctypes.c_ulong]
EOF: bytes
ERROR_NOT_ENOUGH_MEMORY: int
ERROR_OPERATION_ABORTED: int
ERROR_SUCCESS: int
GetCommandLineW: Any
GetConsoleMode: Any
GetLastError: Any
GetStdHandle: Any
HANDLE: Type[ctypes.c_void_p]
LPCWSTR: Type[ctypes.c_wchar_p]
LPWSTR: Type[ctypes.c_wchar_p]
LocalFree: Any
MAX_BYTES_WRITTEN: int
PY2: bool
PyBUF_SIMPLE: int
PyBUF_WRITABLE: int
PyBuffer_Release: ctypes._FuncPointer
PyObject_GetBuffer: ctypes._FuncPointer
ReadConsoleW: Any
STDERR_FILENO: int
STDERR_HANDLE: Any
STDIN_FILENO: int
STDIN_HANDLE: Any
STDOUT_FILENO: int
STDOUT_HANDLE: Any
WINFUNCTYPE: Any
WinError: Any
WriteConsoleW: Any
_NonClosingTextIOWrapper: Type[click._compat._NonClosingTextIOWrapper]
_initial_argv_hash: Any
_stream_factories: Dict[int, Callable[[Any], Any]]
_wrapped_std_streams: set
c_char: Type[ctypes.c_char]
c_char_p: Type[ctypes.c_char_p]
c_int: Type[ctypes.c_int]
c_ssize_t: Type[ctypes.c_ssize_t]
c_ulong: Type[ctypes.c_ulong]
c_void_p: Type[ctypes.c_void_p]
ctypes: module
get_buffer: Optional[Callable]
io: module
kernel32: Any
msvcrt: module
os: module
py_object: Type[ctypes.py_object]
pythonapi: Optional[ctypes.PyDLL]
sys: module
text_type: Type[str]
time: module
windll: Any
zlib: module

_CT = TypeVar('_CT', bound=ctypes._CData)
_CT = TypeVar('_CT', bound=ctypes._CData)

class ConsoleStream:
    _text_stream: Any
    buffer: Any
    name: Any
    def __getattr__(self, name) -> Any: ...
    def __init__(self, text_stream, byte_stream) -> None: ...
    def __repr__(self) -> str: ...
    def isatty(self) -> Any: ...
    def write(self, x) -> Any: ...
    def writelines(self, lines) -> None: ...

class Py_buffer(ctypes.Structure):
    _fields_: List[Tuple[str, Type[Union[ctypes.c_char_p, ctypes.c_int, ctypes.c_ssize_t, ctypes.c_void_p, ctypes.py_object, ctypes.pointer[_CT]]]]]

class WindowsChunkedWriter:
    _WindowsChunkedWriter__wrapped: Any
    __doc__: str
    def __getattr__(self, name) -> Any: ...
    def __init__(self, wrapped) -> None: ...
    def write(self, text) -> None: ...

class _WindowsConsoleRawIOBase(io.RawIOBase):
    handle: Any
    def __init__(self, handle) -> None: ...
    def isatty(self) -> bool: ...

class _WindowsConsoleReader(_WindowsConsoleRawIOBase):
    handle: Any
    def readable(self) -> bool: ...
    def readinto(self, b) -> int: ...

class _WindowsConsoleWriter(_WindowsConsoleRawIOBase):
    handle: Any
    @staticmethod
    def _get_error_message(errno) -> str: ...
    def writable(self) -> bool: ...
    def write(self, b) -> int: ...

def POINTER(type: Type[_CT]) -> Type[ctypes.pointer[_CT]]: ...
def _get_text_stderr(buffer_stream) -> ConsoleStream: ...
def _get_text_stdin(buffer_stream) -> ConsoleStream: ...
def _get_text_stdout(buffer_stream) -> ConsoleStream: ...
def _get_windows_argv() -> Any: ...
def _get_windows_console_stream(f, encoding, errors) -> Any: ...
def _hash_py_argv() -> Any: ...
def _is_console(f) -> bool: ...
def _wrap_std_stream(name) -> None: ...
def byref(obj: ctypes._CData, offset: int = ...) -> ctypes._CArgObject: ...
