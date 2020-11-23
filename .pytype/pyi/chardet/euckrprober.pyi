# (generated with --quick)

import chardet.chardistribution
import chardet.codingstatemachine
import chardet.mbcharsetprober
from typing import Dict, Tuple, Type, Union

CodingStateMachine: Type[chardet.codingstatemachine.CodingStateMachine]
EUCKRDistributionAnalysis: Type[chardet.chardistribution.EUCKRDistributionAnalysis]
EUCKR_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
MultiByteCharSetProber: Type[chardet.mbcharsetprober.MultiByteCharSetProber]

class EUCKRProber(chardet.mbcharsetprober.MultiByteCharSetProber):
    charset_name: str
    coding_sm: chardet.codingstatemachine.CodingStateMachine
    distribution_analyzer: chardet.chardistribution.EUCKRDistributionAnalysis
    language: str
    def __init__(self) -> None: ...
