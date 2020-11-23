# (generated with --quick)

import chardet.chardistribution
import chardet.codingstatemachine
import chardet.mbcharsetprober
from typing import Dict, Tuple, Type, Union

BIG5_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
Big5DistributionAnalysis: Type[chardet.chardistribution.Big5DistributionAnalysis]
CodingStateMachine: Type[chardet.codingstatemachine.CodingStateMachine]
MultiByteCharSetProber: Type[chardet.mbcharsetprober.MultiByteCharSetProber]

class Big5Prober(chardet.mbcharsetprober.MultiByteCharSetProber):
    charset_name: str
    coding_sm: chardet.codingstatemachine.CodingStateMachine
    distribution_analyzer: chardet.chardistribution.Big5DistributionAnalysis
    language: str
    def __init__(self) -> None: ...
