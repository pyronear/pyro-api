# (generated with --quick)

import chardet.charsetprober
import chardet.enums
from typing import Any, Optional, Type, Union

CharSetProber: Type[chardet.charsetprober.CharSetProber]
ProbingState: Type[chardet.enums.ProbingState]

class HebrewProber(chardet.charsetprober.CharSetProber):
    FINAL_KAF: int
    FINAL_MEM: int
    FINAL_NUN: int
    FINAL_PE: int
    FINAL_TSADI: int
    LOGICAL_HEBREW_NAME: str
    MIN_FINAL_CHAR_DISTANCE: int
    MIN_MODEL_DISTANCE: float
    NORMAL_KAF: int
    NORMAL_MEM: int
    NORMAL_NUN: int
    NORMAL_PE: int
    NORMAL_TSADI: int
    VISUAL_HEBREW_NAME: str
    _before_prev: Any
    _final_char_logical_score: Optional[int]
    _final_char_visual_score: Any
    _logical_prober: Any
    _prev: Optional[Union[int, str]]
    _visual_prober: Any
    charset_name: Any
    language: str
    state: int
    def __init__(self) -> None: ...
    def feed(self, byte_str) -> int: ...
    def is_final(self, c) -> bool: ...
    def is_non_final(self, c) -> bool: ...
    def reset(self) -> None: ...
    def set_model_probers(self, logicalProber, visualProber) -> None: ...
