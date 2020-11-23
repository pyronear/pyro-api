# (generated with --quick)

import chardet.charsetprober
import chardet.enums
from typing import Any, List, Type

CharSetProber: Type[chardet.charsetprober.CharSetProber]
ProbingState: Type[chardet.enums.ProbingState]

class CharSetGroupProber(chardet.charsetprober.CharSetProber):
    _active_num: int
    _best_guess_prober: None
    _state: int
    charset_name: Any
    language: Any
    probers: List[nothing]
    def __init__(self, lang_filter = ...) -> None: ...
    def feed(self, byte_str) -> Any: ...
    def get_confidence(self) -> float: ...
    def reset(self) -> None: ...
