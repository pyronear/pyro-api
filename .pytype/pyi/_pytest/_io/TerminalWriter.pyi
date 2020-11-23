# (generated with --quick)

from typing import Any, TextIO

TerminalWriter: Any
final: Any
os: module
shutil: module
sys: module

def get_terminal_width() -> int: ...
def should_do_markup(file: TextIO) -> bool: ...
def wcswidth(s: str) -> int: ...
