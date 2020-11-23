# (generated with --quick)

from typing import Any, Generator, Optional, Tuple

names: Tuple[str, str, str, str]
sys: module

class VendorImporter:
    __doc__: str
    root_name: Any
    search_path: Generator[Any, Any, None]
    vendor_pkg: Any
    vendored_names: set
    def __init__(self, root_name, vendored_names = ..., vendor_pkg = ...) -> None: ...
    def find_module(self, fullname, path = ...) -> Optional[VendorImporter]: ...
    def install(self) -> None: ...
    def load_module(self, fullname) -> module: ...
