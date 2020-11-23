# (generated with --quick)

import __future__
from typing import Any, List

BRAINPOOLP160r1: Curve
BRAINPOOLP192r1: Curve
BRAINPOOLP224r1: Curve
BRAINPOOLP256r1: Curve
BRAINPOOLP320r1: Curve
BRAINPOOLP384r1: Curve
BRAINPOOLP512r1: Curve
NIST192p: Curve
NIST224p: Curve
NIST256p: Curve
NIST384p: Curve
NIST521p: Curve
SECP256k1: Curve
__all__: List[str]
curves: List[Curve]
der: module
division: __future__._Feature
ecdsa: module

class Curve:
    baselen: int
    curve: Any
    encoded_oid: bytes
    generator: Any
    name: Any
    oid: Any
    openssl_name: Any
    order: Any
    signature_length: int
    verifying_key_length: int
    def __init__(self, name, curve, generator, oid, openssl_name = ...) -> None: ...
    def __repr__(self) -> Any: ...

class UnknownCurveError(Exception): ...

def find_curve(oid_curve) -> Curve: ...
def orderlen(order) -> int: ...
