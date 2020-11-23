# (generated with --quick)

from typing import Type

Base64Error: Type[binascii.Error]
PY3: bool
binascii: module

class DecodeError(ParseError):
    __doc__: str

class FileError(FormParserError, OSError):
    __doc__: str

class FormParserError(ValueError):
    __doc__: str

class MultipartParseError(ParseError):
    __doc__: str

class ParseError(FormParserError):
    __doc__: str
    offset: int

class QuerystringParseError(ParseError):
    __doc__: str
