# (generated with --quick)

import chardet.charsetgroupprober
import chardet.hebrewprober
import chardet.sbcharsetprober
from typing import Dict, List, Tuple, Type, Union

CharSetGroupProber: Type[chardet.charsetgroupprober.CharSetGroupProber]
HebrewProber: Type[chardet.hebrewprober.HebrewProber]
Ibm855Model: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Ibm866Model: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Koi8rModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Latin5BulgarianModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Latin5CyrillicModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Latin5TurkishModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Latin7GreekModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
MacCyrillicModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
SingleByteCharSetProber: Type[chardet.sbcharsetprober.SingleByteCharSetProber]
TIS620ThaiModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Win1251BulgarianModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Win1251CyrillicModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Win1253GreekModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]
Win1255HebrewModel: Dict[str, Union[bool, float, str, Tuple[int, ...]]]

class SBCSGroupProber(chardet.charsetgroupprober.CharSetGroupProber):
    probers: List[Union[chardet.hebrewprober.HebrewProber, chardet.sbcharsetprober.SingleByteCharSetProber]]
    def __init__(self) -> None: ...
