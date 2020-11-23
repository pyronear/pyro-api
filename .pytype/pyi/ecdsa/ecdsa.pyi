# (generated with --quick)

import ecdsa.ellipticcurve
from typing import Any, List

_Gx: int
_Gy: int
_a: int
_b: int
_p: int
_q: int
_r: int
curve_192: ecdsa.ellipticcurve.CurveFp
curve_224: ecdsa.ellipticcurve.CurveFp
curve_256: ecdsa.ellipticcurve.CurveFp
curve_384: ecdsa.ellipticcurve.CurveFp
curve_521: ecdsa.ellipticcurve.CurveFp
curve_brainpoolp160r1: ecdsa.ellipticcurve.CurveFp
curve_brainpoolp192r1: ecdsa.ellipticcurve.CurveFp
curve_brainpoolp224r1: ecdsa.ellipticcurve.CurveFp
curve_brainpoolp256r1: ecdsa.ellipticcurve.CurveFp
curve_brainpoolp320r1: ecdsa.ellipticcurve.CurveFp
curve_brainpoolp384r1: ecdsa.ellipticcurve.CurveFp
curve_brainpoolp512r1: ecdsa.ellipticcurve.CurveFp
curve_secp256k1: ecdsa.ellipticcurve.CurveFp
ellipticcurve: module
generator_192: ecdsa.ellipticcurve.Point
generator_224: ecdsa.ellipticcurve.Point
generator_256: ecdsa.ellipticcurve.Point
generator_384: ecdsa.ellipticcurve.Point
generator_521: ecdsa.ellipticcurve.Point
generator_brainpoolp160r1: ecdsa.ellipticcurve.Point
generator_brainpoolp192r1: ecdsa.ellipticcurve.Point
generator_brainpoolp224r1: ecdsa.ellipticcurve.Point
generator_brainpoolp256r1: ecdsa.ellipticcurve.Point
generator_brainpoolp320r1: ecdsa.ellipticcurve.Point
generator_brainpoolp384r1: ecdsa.ellipticcurve.Point
generator_brainpoolp512r1: ecdsa.ellipticcurve.Point
generator_secp256k1: ecdsa.ellipticcurve.Point
numbertheory: module

class Private_key:
    __doc__: str
    public_key: Any
    secret_multiplier: Any
    def __init__(self, public_key, secret_multiplier) -> None: ...
    def sign(self, hash, random_k) -> Signature: ...

class Public_key:
    __doc__: str
    curve: Any
    generator: Any
    point: Any
    def __init__(self, generator, point) -> None: ...
    def verifies(self, hash, signature) -> Any: ...

class RSZeroError(RuntimeError): ...

class Signature:
    __doc__: str
    r: Any
    s: Any
    def __init__(self, r, s) -> None: ...
    def recover_public_keys(self, hash, generator) -> List[Public_key]: ...

def b(s) -> Any: ...
def bit_length(num) -> int: ...
def digest_integer(m) -> Any: ...
def int2byte(*v) -> bytes: ...
def int_to_string(x) -> Any: ...
def point_is_valid(generator, x, y) -> bool: ...
def string_to_int(s) -> Any: ...
