# (generated with --quick)

import chardet.charsetgroupprober
import chardet.enums
import chardet.escprober
import chardet.latin1prober
import chardet.mbcsgroupprober
import chardet.sbcsgroupprober
from typing import Any, Dict, List, Optional, Pattern, Type, Union

CharSetGroupProber: Type[chardet.charsetgroupprober.CharSetGroupProber]
EscCharSetProber: Type[chardet.escprober.EscCharSetProber]
InputState: Type[chardet.enums.InputState]
LanguageFilter: Type[chardet.enums.LanguageFilter]
Latin1Prober: Type[chardet.latin1prober.Latin1Prober]
MBCSGroupProber: Type[chardet.mbcsgroupprober.MBCSGroupProber]
ProbingState: Type[chardet.enums.ProbingState]
SBCSGroupProber: Type[chardet.sbcsgroupprober.SBCSGroupProber]
codecs: module
logging: module
re: module

class UniversalDetector:
    ESC_DETECTOR: Pattern[bytes]
    HIGH_BYTE_DETECTOR: Pattern[bytes]
    ISO_WIN_MAP: Dict[str, str]
    MINIMUM_THRESHOLD: float
    WIN_BYTE_DETECTOR: Pattern[bytes]
    __doc__: str
    _charset_probers: List[Union[chardet.latin1prober.Latin1Prober, chardet.mbcsgroupprober.MBCSGroupProber, chardet.sbcsgroupprober.SBCSGroupProber]]
    _esc_charset_prober: Optional[chardet.escprober.EscCharSetProber]
    _got_data: Optional[bool]
    _has_win_bytes: Optional[bool]
    _input_state: Optional[int]
    _last_char: Any
    done: Optional[bool]
    lang_filter: Any
    logger: logging.Logger
    result: Optional[Dict[str, Any]]
    def __init__(self, lang_filter = ...) -> None: ...
    def close(self) -> Any: ...
    def feed(self, byte_str) -> None: ...
    def reset(self) -> None: ...
