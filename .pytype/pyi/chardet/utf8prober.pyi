# (generated with --quick)

import chardet.charsetprober
import chardet.codingstatemachine
import chardet.enums
from typing import Any, Dict, Tuple, Type, Union

CharSetProber: Type[chardet.charsetprober.CharSetProber]
CodingStateMachine: Type[chardet.codingstatemachine.CodingStateMachine]
MachineState: Type[chardet.enums.MachineState]
ProbingState: Type[chardet.enums.ProbingState]
UTF8_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]

class UTF8Prober(chardet.charsetprober.CharSetProber):
    ONE_CHAR_PROB: float
    _num_mb_chars: Any
    _state: int
    charset_name: str
    coding_sm: chardet.codingstatemachine.CodingStateMachine
    language: str
    def __init__(self) -> None: ...
    def feed(self, byte_str) -> Any: ...
    def get_confidence(self) -> Any: ...
    def reset(self) -> None: ...
