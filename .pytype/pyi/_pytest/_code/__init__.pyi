# (generated with --quick)

import _pytest._code.code
import _pytest._code.source
from typing import Any, List, Tuple, Type

Code: Type[_pytest._code.code.Code]
ExceptionInfo: Any
Frame: Type[_pytest._code.code.Frame]
Source: Type[_pytest._code.source.Source]
Traceback: Type[_pytest._code.code.Traceback]
TracebackEntry: Type[_pytest._code.code.TracebackEntry]
__all__: List[str]

def filter_traceback(entry: _pytest._code.code.TracebackEntry) -> bool: ...
def getfslineno(obj: object) -> Tuple[Any, int]: ...
def getrawcode(obj, trycall: bool = ...) -> Any: ...
