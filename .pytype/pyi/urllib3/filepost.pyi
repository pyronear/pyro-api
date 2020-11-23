# (generated with --quick)

import __future__
import io
from typing import Any, Generator, Tuple, Type, Union
import urllib3.fields

BytesIO: Type[io.BytesIO]
RequestField: Type[urllib3.fields.RequestField]
absolute_import: __future__._Feature
binascii: module
codecs: module
os: module
six: module
writer: codecs._StreamWriter

def b(s) -> Any: ...
def choose_boundary() -> Union[bytes, str]: ...
def encode_multipart_formdata(fields, boundary = ...) -> Tuple[bytes, str]: ...
def iter_field_objects(fields) -> Generator[Any, Any, None]: ...
def iter_fields(fields) -> Any: ...
