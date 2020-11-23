# (generated with --quick)

import contextlib
from typing import Any, Callable, Iterator, TypeVar

textwrap: module

_T = TypeVar('_T')

class TextWrapper(textwrap.TextWrapper):
    extra_indent: Callable[..., contextlib._GeneratorContextManager]
    def _handle_long_word(self, reversed_chunks, cur_line, cur_len, width) -> None: ...
    def indent_only(self, text) -> str: ...

def contextmanager(func: Callable[..., Iterator[_T]]) -> Callable[..., contextlib._GeneratorContextManager[_T]]: ...
