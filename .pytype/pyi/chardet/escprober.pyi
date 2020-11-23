# (generated with --quick)

import chardet.charsetprober
import chardet.codingstatemachine
import chardet.enums
from typing import Any, Dict, List, Optional, Tuple, Type, Union

CharSetProber: Type[chardet.charsetprober.CharSetProber]
CodingStateMachine: Type[chardet.codingstatemachine.CodingStateMachine]
HZ_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
ISO2022CN_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
ISO2022JP_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
ISO2022KR_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
LanguageFilter: Type[chardet.enums.LanguageFilter]
MachineState: Type[chardet.enums.MachineState]
ProbingState: Type[chardet.enums.ProbingState]

class EscCharSetProber(chardet.charsetprober.CharSetProber):
    __doc__: str
    _detected_charset: Any
    _detected_language: Any
    _state: Optional[int]
    active_sm_count: Any
    charset_name: Any
    coding_sm: List[chardet.codingstatemachine.CodingStateMachine]
    language: Any
    def __init__(self, lang_filter = ...) -> None: ...
    def feed(self, byte_str) -> Any: ...
    def get_confidence(self) -> float: ...
    def reset(self) -> None: ...
