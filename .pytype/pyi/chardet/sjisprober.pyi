# (generated with --quick)

import chardet.chardistribution
import chardet.codingstatemachine
import chardet.enums
import chardet.jpcntx
import chardet.mbcharsetprober
from typing import Any, Dict, Tuple, Type, Union

CodingStateMachine: Type[chardet.codingstatemachine.CodingStateMachine]
MachineState: Type[chardet.enums.MachineState]
MultiByteCharSetProber: Type[chardet.mbcharsetprober.MultiByteCharSetProber]
ProbingState: Type[chardet.enums.ProbingState]
SJISContextAnalysis: Type[chardet.jpcntx.SJISContextAnalysis]
SJISDistributionAnalysis: Type[chardet.chardistribution.SJISDistributionAnalysis]
SJIS_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]

class SJISProber(chardet.mbcharsetprober.MultiByteCharSetProber):
    _state: int
    charset_name: Any
    coding_sm: chardet.codingstatemachine.CodingStateMachine
    context_analyzer: chardet.jpcntx.SJISContextAnalysis
    distribution_analyzer: chardet.chardistribution.SJISDistributionAnalysis
    language: str
    def __init__(self) -> None: ...
    def feed(self, byte_str) -> Any: ...
    def get_confidence(self) -> Any: ...
    def reset(self) -> None: ...
