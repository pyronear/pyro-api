# (generated with --quick)

import click.exceptions
import collections
from typing import Any, Dict, List, NoReturn, Tuple, Type, TypeVar

BadArgumentUsage: Type[click.exceptions.BadArgumentUsage]
BadOptionUsage: Type[click.exceptions.BadOptionUsage]
NoSuchOption: Type[click.exceptions.NoSuchOption]
UsageError: Type[click.exceptions.UsageError]
deque: Type[collections.deque]
re: module

_T0 = TypeVar('_T0')

class Argument:
    dest: Any
    nargs: Any
    obj: Any
    def __init__(self, dest, nargs = ..., obj = ...) -> None: ...
    def process(self, value, state) -> None: ...

class Option:
    _long_opts: list
    _short_opts: list
    action: Any
    const: Any
    dest: Any
    nargs: Any
    obj: Any
    prefixes: set
    takes_value: bool
    def __init__(self, opts, dest, action = ..., nargs = ..., const = ..., obj = ...) -> None: ...
    def process(self, value, state) -> None: ...

class OptionParser:
    __doc__: str
    _args: List[Argument]
    _long_opt: Dict[Any, Option]
    _opt_prefixes: set
    _short_opt: Dict[Any, Option]
    allow_interspersed_args: Any
    ctx: Any
    ignore_unknown_options: Any
    def __init__(self, ctx = ...) -> None: ...
    def _match_long_opt(self, opt, explicit_value, state) -> None: ...
    def _match_short_opt(self, arg, state) -> None: ...
    def _process_args_for_args(self, state) -> None: ...
    def _process_args_for_options(self, state) -> None: ...
    def _process_opts(self, arg, state) -> Any: ...
    def add_argument(self, dest, nargs = ..., obj = ...) -> None: ...
    def add_option(self, opts, dest, action = ..., nargs = ..., const = ..., obj = ...) -> None: ...
    def parse_args(self, args) -> Tuple[Dict[nothing, nothing], List[nothing], List[nothing]]: ...

class ParsingState:
    largs: List[nothing]
    opts: Dict[nothing, nothing]
    order: List[nothing]
    rargs: Any
    def __init__(self, rargs) -> None: ...

def _error_opt_args(nargs, opt) -> NoReturn: ...
def _unpack_args(args, nargs_spec) -> Tuple[tuple, list]: ...
def normalize_opt(opt, ctx) -> Any: ...
def split_arg_string(string) -> list: ...
def split_opt(opt: _T0) -> Tuple[Any, Any]: ...
