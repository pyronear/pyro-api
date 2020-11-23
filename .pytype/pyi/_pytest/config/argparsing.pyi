# (generated with --quick)

import __builtin__
import typing
from typing import Any, Dict, List, Mapping, NoReturn, Optional, Sequence, Tuple, Type, Union

FILE_OR_DIR: str
Literal: Type[typing.Literal]
Parser: Any
TYPE_CHECKING: Any
UsageError: Any
_pytest: module
argparse: module
final: Any
py: module
sys: module
warnings: module

class Argument:
    __doc__: str
    _attrs: Dict[str, Any]
    _long_opts: List[str]
    _short_opts: List[str]
    _typ_map: Dict[str, __builtin__.type[Union[complex, float, int, str]]]
    default: Any
    dest: Any
    type: Any
    def __init__(self, *names: str, **attrs) -> None: ...
    def __repr__(self) -> str: ...
    def _set_opt_strings(self, opts: Sequence[str]) -> None: ...
    def attrs(self) -> Mapping[str, Any]: ...
    def names(self) -> List[str]: ...

class ArgumentError(Exception):
    __doc__: str
    msg: str
    option_id: str
    def __init__(self, msg: str, option: Union[Argument, str]) -> None: ...
    def __str__(self) -> str: ...

class DropShorterLongHelpFormatter(argparse.HelpFormatter):
    __doc__: str
    def __init__(self, *args, **kwargs) -> None: ...
    def _format_action_invocation(self, action: argparse.Action) -> str: ...
    def _split_lines(self, text, width) -> List[str]: ...

class MyOptionParser(argparse.ArgumentParser):
    _parser: Any
    extra_info: Dict[str, Any]
    def __init__(self, parser, extra_info: Optional[Dict[str, Any]] = ..., prog: Optional[str] = ...) -> None: ...
    def _parse_optional(self, arg_string: str) -> Optional[Tuple[Optional[argparse.Action], str, Optional[str]]]: ...
    def error(self, message: str) -> NoReturn: ...
    def parse_args(self, args: Optional[Sequence[str]] = ..., namespace: Optional[argparse.Namespace] = ...) -> argparse.Namespace: ...

class OptionGroup:
    description: str
    name: str
    options: List[Argument]
    parser: Any
    def __init__(self, name: str, description: str = ..., parser = ...) -> None: ...
    def _addoption(self, *optnames: str, **attrs) -> None: ...
    def _addoption_instance(self, option: Argument, shortupper: bool = ...) -> None: ...
    def addoption(self, *optnames: str, **attrs) -> None: ...

def gettext(message: str) -> str: ...
