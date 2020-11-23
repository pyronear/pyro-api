# (generated with --quick)

from typing import Any, List, Optional, TypeVar

argcomplete: Any
argparse: module
filescompleter: Optional[FastFilesCompleter]
os: module
sys: module

AnyStr = TypeVar('AnyStr', str, bytes)

class FastFilesCompleter:
    __doc__: str
    directories: bool
    def __call__(self, prefix: str, **kwargs) -> List[str]: ...
    def __init__(self, directories: bool = ...) -> None: ...

def glob(pathname: AnyStr, *, recursive: bool = ...) -> List[AnyStr]: ...
def try_argcomplete(parser: argparse.ArgumentParser) -> None: ...
