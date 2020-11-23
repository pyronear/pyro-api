# (generated with --quick)

import chardet.chardistribution
import chardet.codingstatemachine
import chardet.mbcharsetprober
from typing import Dict, Tuple, Type, Union

CodingStateMachine: Type[chardet.codingstatemachine.CodingStateMachine]
EUCTWDistributionAnalysis: Type[chardet.chardistribution.EUCTWDistributionAnalysis]
EUCTW_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
MultiByteCharSetProber: Type[chardet.mbcharsetprober.MultiByteCharSetProber]

class EUCTWProber(chardet.mbcharsetprober.MultiByteCharSetProber):
    charset_name: str
    coding_sm: chardet.codingstatemachine.CodingStateMachine
    distribution_analyzer: chardet.chardistribution.EUCTWDistributionAnalysis
    language: str
    def __init__(self) -> None: ...
