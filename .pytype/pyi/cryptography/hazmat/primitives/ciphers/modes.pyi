# (generated with --quick)

import __future__
from typing import Any

CBC: Any
CFB: Any
CFB8: Any
CTR: Any
ECB: Any
GCM: Any
OFB: Any
XTS: Any
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module
utils: module

class Mode(metaclass=abc.ABCMeta):
    name: Any
    @abstractmethod
    def validate_for_algorithm(self, algorithm) -> Any: ...

class ModeWithAuthenticationTag(metaclass=abc.ABCMeta):
    tag: Any

class ModeWithInitializationVector(metaclass=abc.ABCMeta):
    initialization_vector: Any

class ModeWithNonce(metaclass=abc.ABCMeta):
    nonce: Any

class ModeWithTweak(metaclass=abc.ABCMeta):
    tweak: Any

def _check_aes_key_length(self, algorithm) -> None: ...
def _check_iv_and_key_length(self, algorithm) -> None: ...
def _check_iv_length(self, algorithm) -> None: ...
