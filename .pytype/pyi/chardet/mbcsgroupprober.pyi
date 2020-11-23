# (generated with --quick)

import chardet.big5prober
import chardet.charsetgroupprober
import chardet.cp949prober
import chardet.eucjpprober
import chardet.euckrprober
import chardet.euctwprober
import chardet.gb2312prober
import chardet.sjisprober
import chardet.utf8prober
from typing import Type

Big5Prober: Type[chardet.big5prober.Big5Prober]
CP949Prober: Type[chardet.cp949prober.CP949Prober]
CharSetGroupProber: Type[chardet.charsetgroupprober.CharSetGroupProber]
EUCJPProber: Type[chardet.eucjpprober.EUCJPProber]
EUCKRProber: Type[chardet.euckrprober.EUCKRProber]
EUCTWProber: Type[chardet.euctwprober.EUCTWProber]
GB2312Prober: Type[chardet.gb2312prober.GB2312Prober]
SJISProber: Type[chardet.sjisprober.SJISProber]
UTF8Prober: Type[chardet.utf8prober.UTF8Prober]

class MBCSGroupProber(chardet.charsetgroupprober.CharSetGroupProber):
    probers: list
    def __init__(self, lang_filter = ...) -> None: ...
