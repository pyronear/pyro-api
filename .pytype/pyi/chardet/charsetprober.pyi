# (generated with --quick)

import chardet.enums
from typing import Any, Optional, Type

ProbingState: Type[chardet.enums.ProbingState]
logging: module
re: module

class CharSetProber:
    SHORTCUT_THRESHOLD: float
    _state: Optional[int]
    charset_name: None
    lang_filter: Any
    logger: logging.Logger
    state: Any
    def __init__(self, lang_filter = ...) -> None: ...
    def feed(self, buf) -> None: ...
    @staticmethod
    def filter_high_byte_only(buf) -> bytes: ...
    @staticmethod
    def filter_international_words(buf) -> bytearray: ...
    @staticmethod
    def filter_with_english_letters(buf) -> bytearray: ...
    def get_confidence(self) -> float: ...
    def reset(self) -> None: ...
