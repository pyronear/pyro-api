# (generated with --quick)

import __future__
import multipart.multipart
from typing import Type

FormParser: Type[multipart.multipart.FormParser]
MultipartParser: Type[multipart.multipart.MultipartParser]
OctetStreamParser: Type[multipart.multipart.OctetStreamParser]
QuerystringParser: Type[multipart.multipart.QuerystringParser]
__author__: str
__copyright__: str
__license__: str
__version__: str
absolute_import: __future__._Feature
sys: module

def create_form_parser(headers, on_field, on_file, trust_x_headers = ..., config = ...) -> multipart.multipart.FormParser: ...
def parse_form(headers, input_stream, on_field, on_file, chunk_size = ..., **kwargs) -> None: ...
