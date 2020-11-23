# (generated with --quick)

import chardet.enums
from typing import Any, Type

MachineState: Type[chardet.enums.MachineState]
logging: module

class CodingStateMachine:
    __doc__: str
    _curr_byte_pos: int
    _curr_char_len: Any
    _curr_state: Any
    _model: Any
    language: Any
    logger: logging.Logger
    def __init__(self, sm) -> None: ...
    def get_coding_state_machine(self) -> Any: ...
    def get_current_charlen(self) -> int: ...
    def next_state(self, c) -> Any: ...
    def reset(self) -> None: ...
