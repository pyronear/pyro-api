# (generated with --quick)

import __future__
import cryptography.x509.name
from typing import Any, Dict, Optional, Tuple, Type

DNSName: Any
DirectoryName: Any
IPAddress: Any
Name: Type[cryptography.x509.name.Name]
ObjectIdentifier: Any
OtherName: Any
RFC822Name: Any
RegisteredID: Any
UniformResourceIdentifier: Any
_GENERAL_NAMES: Dict[int, str]
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
ipaddress: module
print_function: __future__._Feature
six: module
utils: module

class GeneralName(metaclass=abc.ABCMeta):
    value: Any

class UnsupportedGeneralNameType(Exception):
    type: Any
    def __init__(self, msg, type) -> None: ...

def parseaddr(address: Optional[str]) -> Tuple[str, str]: ...
