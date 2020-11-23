# (generated with --quick)

import __future__
import io
import multipart.decoders
import multipart.exceptions
import numbers
from typing import Any, BinaryIO, Dict, FrozenSet, IO, List, Optional, Pattern, Tuple, Type, TypeVar, Union

AMPERSAND: int
Base64Decoder: Type[multipart.decoders.Base64Decoder]
Base64Error: Type[binascii.Error]
BytesIO: Type[io.BytesIO]
COLON: int
CR: int
DecodeError: Type[multipart.exceptions.DecodeError]
FLAG_LAST_BOUNDARY: int
FLAG_PART_BOUNDARY: int
FileError: Type[multipart.exceptions.FileError]
FormParserError: Type[multipart.exceptions.FormParserError]
HYPHEN: int
LF: int
LOWER_A: int
LOWER_Z: int
MultipartParseError: Type[multipart.exceptions.MultipartParseError]
NULL: int
Number: Type[numbers.Number]
OPTION_RE: Pattern[bytes]
OPTION_RE_STR: bytes
PY3: bool
ParseError: Type[multipart.exceptions.ParseError]
QUOTE: int
QUOTED_STR: bytes
QuerystringParseError: Type[multipart.exceptions.QuerystringParseError]
QuotedPrintableDecoder: Type[multipart.decoders.QuotedPrintableDecoder]
SEMICOLON: int
SPACE: int
SPECIAL_CHARS: bytes
STATES: List[str]
STATE_BEFORE_FIELD: int
STATE_END: int
STATE_FIELD_DATA: int
STATE_FIELD_NAME: int
STATE_HEADERS_ALMOST_DONE: int
STATE_HEADER_FIELD: int
STATE_HEADER_FIELD_START: int
STATE_HEADER_VALUE: int
STATE_HEADER_VALUE_ALMOST_DONE: int
STATE_HEADER_VALUE_START: int
STATE_PART_DATA: int
STATE_PART_DATA_END: int
STATE_PART_DATA_START: int
STATE_START: int
STATE_START_BOUNDARY: int
VALUE_STR: bytes
_missing: Any
absolute_import: __future__._Feature
base64: module
binary_type: Type[bytes]
binascii: module
logging: module
os: module
parse_qs: Any
print_function: __future__._Feature
re: module
shutil: module
sys: module
tempfile: module
text_type: Type[str]
with_statement: __future__._Feature

_T0 = TypeVar('_T0')
_T1 = TypeVar('_T1')
_TField = TypeVar('_TField', bound=Field)

class BaseParser:
    __doc__: str
    logger: logging.Logger
    def __init__(self) -> None: ...
    def __repr__(self) -> str: ...
    def callback(self, name, data = ..., start = ..., end = ...) -> None: ...
    def close(self) -> None: ...
    def finalize(self) -> None: ...
    def set_callback(self, name, new_func) -> None: ...

class Field:
    __doc__: str
    _cache: Any
    _name: Any
    _value: list
    field_name: Any
    value: Any
    def __eq__(self, other) -> Any: ...
    def __init__(self, name) -> None: ...
    def __repr__(self) -> str: ...
    def close(self) -> None: ...
    def finalize(self) -> None: ...
    @classmethod
    def from_value(klass: Type[_TField], name, value) -> _TField: ...
    def on_data(self, data) -> int: ...
    def on_end(self) -> None: ...
    def set_none(self) -> None: ...
    def write(self, data) -> Any: ...

class File:
    __doc__: str
    _actual_file_name: Any
    _bytes_written: Any
    _config: Any
    _ext: Any
    _field_name: Any
    _file_base: Any
    _file_name: Any
    _fileobj: Any
    _in_memory: bool
    actual_file_name: Any
    field_name: Any
    file_name: Any
    file_object: Any
    in_memory: Any
    logger: logging.Logger
    size: Any
    def __init__(self, file_name, field_name = ..., config = ...) -> None: ...
    def __repr__(self) -> str: ...
    def _get_disk_file(self) -> Union[BinaryIO, IO[Union[bytes, str]]]: ...
    def close(self) -> None: ...
    def finalize(self) -> None: ...
    def flush_to_disk(self) -> None: ...
    def on_data(self, data) -> Any: ...
    def on_end(self) -> None: ...
    def write(self, data) -> Any: ...

class FormParser:
    DEFAULT_CONFIG: Dict[str, Optional[Union[float, int]]]
    FieldClass: Type[Field]
    FileClass: Type[File]
    __doc__: str
    boundary: Any
    bytes_received: int
    config: dict
    content_type: Any
    logger: logging.Logger
    on_end: Any
    on_field: Any
    on_file: Any
    parser: Optional[Union[MultipartParser, OctetStreamParser, QuerystringParser]]
    def __init__(self, content_type, on_field, on_file, on_end = ..., boundary = ..., file_name = ..., FileClass = ..., FieldClass = ..., config = ...) -> None: ...
    def __repr__(self) -> str: ...
    def close(self) -> None: ...
    def finalize(self) -> None: ...
    def write(self, data) -> Any: ...

class MultipartParser(BaseParser):
    __doc__: str
    _current_size: Any
    boundary: bytes
    boundary_chars: FrozenSet[int]
    callbacks: Any
    flags: int
    index: int
    logger: logging.Logger
    lookbehind: Any
    marks: Dict[Any, int]
    max_size: Any
    state: int
    def __init__(self, boundary, callbacks = ..., max_size = ...) -> None: ...
    def __repr__(self) -> str: ...
    def _internal_write(self, data, length: _T1) -> _T1: ...
    def finalize(self) -> None: ...
    def write(self, data) -> Any: ...

class OctetStreamParser(BaseParser):
    __doc__: str
    _current_size: int
    _started: bool
    callbacks: Any
    logger: logging.Logger
    max_size: Any
    def __init__(self, callbacks = ..., max_size = ...) -> None: ...
    def __repr__(self) -> str: ...
    def finalize(self) -> None: ...
    def write(self, data) -> int: ...

class QuerystringParser(BaseParser):
    __doc__: str
    _current_size: Any
    _found_sep: bool
    callbacks: Any
    logger: logging.Logger
    max_size: Any
    state: int
    strict_parsing: Any
    def __init__(self, callbacks = ..., strict_parsing = ..., max_size = ...) -> None: ...
    def __repr__(self) -> str: ...
    def _internal_write(self, data, length) -> int: ...
    def finalize(self) -> None: ...
    def write(self, data) -> Any: ...

def create_form_parser(headers, on_field, on_file, trust_x_headers = ..., config = ...) -> FormParser: ...
def join_bytes(b) -> bytes: ...
def lower_char(c) -> Any: ...
def ord_char(c: _T0) -> _T0: ...
def parse_form(headers, input_stream, on_field, on_file, chunk_size = ..., **kwargs) -> None: ...
def parse_options_header(value) -> Tuple[Any, Dict[bytes, bytes]]: ...
