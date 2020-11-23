# (generated with --quick)

import chardet.chardistribution
import chardet.codingstatemachine
import chardet.mbcharsetprober
from typing import Dict, Tuple, Type, Union

CodingStateMachine: Type[chardet.codingstatemachine.CodingStateMachine]
GB2312DistributionAnalysis: Type[chardet.chardistribution.GB2312DistributionAnalysis]
GB2312_SM_MODEL: Dict[str, Union[int, str, Tuple[int, ...]]]
MultiByteCharSetProber: Type[chardet.mbcharsetprober.MultiByteCharSetProber]

class GB2312Prober(chardet.mbcharsetprober.MultiByteCharSetProber):
    charset_name: str
    coding_sm: chardet.codingstatemachine.CodingStateMachine
    distribution_analyzer: chardet.chardistribution.GB2312DistributionAnalysis
    language: str
    def __init__(self) -> None: ...
