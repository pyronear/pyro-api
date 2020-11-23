# (generated with --quick)

import chardet.charsetprober
import chardet.enums
from typing import Any, List, Optional, Type

CharSetProber: Type[chardet.charsetprober.CharSetProber]
CharacterCategory: Type[chardet.enums.CharacterCategory]
ProbingState: Type[chardet.enums.ProbingState]
SequenceLikelihood: Type[chardet.enums.SequenceLikelihood]

class SingleByteCharSetProber(chardet.charsetprober.CharSetProber):
    NEGATIVE_SHORTCUT_THRESHOLD: float
    POSITIVE_SHORTCUT_THRESHOLD: float
    SAMPLE_SIZE: int
    SB_ENOUGH_REL_THRESHOLD: int
    _freq_char: Any
    _last_order: Any
    _model: Any
    _name_prober: Any
    _reversed: Any
    _seq_counters: Optional[List[int]]
    _state: int
    _total_char: Any
    _total_seqs: Any
    charset_name: Any
    language: Any
    def __init__(self, model, reversed = ..., name_prober = ...) -> None: ...
    def feed(self, byte_str) -> Any: ...
    def get_confidence(self) -> Any: ...
    def reset(self) -> None: ...
