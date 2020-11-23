# (generated with --quick)

import __future__
from typing import Any, List, NoReturn, Set, Tuple

__all__: List[str]
absolute_import: __future__._Feature
urlencode: Any

class RequestMethods:
    __doc__: str
    _encode_url_methods: Set[str]
    headers: Any
    def __init__(self, headers = ...) -> None: ...
    def request(self, method, url, fields = ..., headers = ..., **urlopen_kw) -> Any: ...
    def request_encode_body(self, method, url, fields = ..., headers = ..., encode_multipart = ..., multipart_boundary = ..., **urlopen_kw) -> Any: ...
    def request_encode_url(self, method, url, fields = ..., headers = ..., **urlopen_kw) -> Any: ...
    def urlopen(self, method, url, body = ..., headers = ..., encode_multipart = ..., multipart_boundary = ..., **kw) -> NoReturn: ...

def encode_multipart_formdata(fields, boundary = ...) -> Tuple[bytes, str]: ...
