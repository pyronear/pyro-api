# (generated with --quick)

import chardet.charsetprober
import chardet.enums
from typing import Any, Type

CharSetProber: Type[chardet.charsetprober.CharSetProber]
MachineState: Type[chardet.enums.MachineState]
ProbingState: Type[chardet.enums.ProbingState]

class MultiByteCharSetProber(chardet.charsetprober.CharSetProber):
    __doc__: str
    _last_char: list
    _state: int
    coding_sm: None
    distribution_analyzer: None
    def __init__(self, lang_filter = ...) -> None: ...
    def feed(self, byte_str) -> Any: ...
    def get_confidence(self) -> Any: ...
    def reset(self) -> None: ...
