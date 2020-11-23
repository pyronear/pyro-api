# (generated with --quick)

import chardet.chardistribution
import chardet.codingstatemachine
import chardet.mbcharsetprober
from typing import Dict, Tuple, Type, Union

CP949_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
CodingStateMachine: Type[chardet.codingstatemachine.CodingStateMachine]
EUCKRDistributionAnalysis: Type[chardet.chardistribution.EUCKRDistributionAnalysis]
MultiByteCharSetProber: Type[chardet.mbcharsetprober.MultiByteCharSetProber]

class CP949Prober(chardet.mbcharsetprober.MultiByteCharSetProber):
    charset_name: str
    coding_sm: chardet.codingstatemachine.CodingStateMachine
    distribution_analyzer: chardet.chardistribution.EUCKRDistributionAnalysis
    language: str
    def __init__(self) -> None: ...
