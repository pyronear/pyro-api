# (generated with --quick)

import __future__
import enum
from typing import Any, Type

Enum: Type[enum.Enum]
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module

class LogEntryType(enum.Enum):
    PRE_CERTIFICATE: int
    X509_CERTIFICATE: int

class SignedCertificateTimestamp(metaclass=abc.ABCMeta):
    entry_type: Any
    log_id: Any
    timestamp: Any
    version: Any

class Version(enum.Enum):
    v1: int
