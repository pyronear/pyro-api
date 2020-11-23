# (generated with --quick)

import __future__
import cryptography.hazmat._oid
from typing import Any, Dict, Type, TypeVar

EllipticCurvePublicKeyWithSerialization = EllipticCurvePublicKey

BrainpoolP256R1: Any
BrainpoolP384R1: Any
BrainpoolP512R1: Any
ECDSA: Any
ObjectIdentifier: Type[cryptography.hazmat._oid.ObjectIdentifier]
SECP192R1: Any
SECP224R1: Any
SECP256K1: Any
SECP256R1: Any
SECP384R1: Any
SECP521R1: Any
SECT163K1: Any
SECT163R2: Any
SECT233K1: Any
SECT233R1: Any
SECT283K1: Any
SECT283R1: Any
SECT409K1: Any
SECT409R1: Any
SECT571K1: Any
SECT571R1: Any
_CURVE_TYPES: Dict[str, Any]
_OID_TO_CURVE: Dict[cryptography.hazmat._oid.ObjectIdentifier, Any]
abc: module
absolute_import: __future__._Feature
division: __future__._Feature
print_function: __future__._Feature
six: module
utils: module
warnings: module

_TEllipticCurvePublicNumbers = TypeVar('_TEllipticCurvePublicNumbers', bound=EllipticCurvePublicNumbers)

class ECDH: ...

class EllipticCurve(metaclass=abc.ABCMeta):
    key_size: Any
    name: Any

class EllipticCurveOID:
    BRAINPOOLP256R1: cryptography.hazmat._oid.ObjectIdentifier
    BRAINPOOLP384R1: cryptography.hazmat._oid.ObjectIdentifier
    BRAINPOOLP512R1: cryptography.hazmat._oid.ObjectIdentifier
    SECP192R1: cryptography.hazmat._oid.ObjectIdentifier
    SECP224R1: cryptography.hazmat._oid.ObjectIdentifier
    SECP256K1: cryptography.hazmat._oid.ObjectIdentifier
    SECP256R1: cryptography.hazmat._oid.ObjectIdentifier
    SECP384R1: cryptography.hazmat._oid.ObjectIdentifier
    SECP521R1: cryptography.hazmat._oid.ObjectIdentifier
    SECT163K1: cryptography.hazmat._oid.ObjectIdentifier
    SECT163R2: cryptography.hazmat._oid.ObjectIdentifier
    SECT233K1: cryptography.hazmat._oid.ObjectIdentifier
    SECT233R1: cryptography.hazmat._oid.ObjectIdentifier
    SECT283K1: cryptography.hazmat._oid.ObjectIdentifier
    SECT283R1: cryptography.hazmat._oid.ObjectIdentifier
    SECT409K1: cryptography.hazmat._oid.ObjectIdentifier
    SECT409R1: cryptography.hazmat._oid.ObjectIdentifier
    SECT571K1: cryptography.hazmat._oid.ObjectIdentifier
    SECT571R1: cryptography.hazmat._oid.ObjectIdentifier

class EllipticCurvePrivateKey(metaclass=abc.ABCMeta):
    curve: Any
    key_size: Any
    @abstractmethod
    def exchange(self, algorithm, peer_public_key) -> Any: ...
    @abstractmethod
    def public_key(self) -> Any: ...
    @abstractmethod
    def sign(self, data, signature_algorithm) -> Any: ...
    @abstractmethod
    def signer(self, signature_algorithm) -> Any: ...

class EllipticCurvePrivateKeyWithSerialization(EllipticCurvePrivateKey):
    @abstractmethod
    def private_bytes(self, encoding, format, encryption_algorithm) -> Any: ...
    @abstractmethod
    def private_numbers(self) -> Any: ...

class EllipticCurvePrivateNumbers:
    _private_value: Any
    _public_numbers: Any
    private_value: Any
    public_numbers: Any
    def __eq__(self, other) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, private_value, public_numbers) -> None: ...
    def __ne__(self, other) -> bool: ...
    def private_key(self, backend = ...) -> Any: ...

class EllipticCurvePublicKey(metaclass=abc.ABCMeta):
    curve: Any
    key_size: Any
    @classmethod
    def from_encoded_point(cls, curve, data) -> Any: ...
    @abstractmethod
    def public_bytes(self, encoding, format) -> Any: ...
    @abstractmethod
    def public_numbers(self) -> Any: ...
    @abstractmethod
    def verifier(self, signature, signature_algorithm) -> Any: ...
    @abstractmethod
    def verify(self, signature, data, signature_algorithm) -> Any: ...

class EllipticCurvePublicNumbers:
    _curve: Any
    _x: Any
    _y: Any
    curve: Any
    x: Any
    y: Any
    def __eq__(self, other) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, x, y, curve) -> None: ...
    def __ne__(self, other) -> bool: ...
    def __repr__(self) -> str: ...
    def encode_point(self) -> bytes: ...
    @classmethod
    def from_encoded_point(cls: Type[_TEllipticCurvePublicNumbers], curve, data) -> _TEllipticCurvePublicNumbers: ...
    def public_key(self, backend = ...) -> Any: ...

class EllipticCurveSignatureAlgorithm(metaclass=abc.ABCMeta):
    algorithm: Any

def _get_backend(backend) -> Any: ...
def derive_private_key(private_value, curve, backend = ...) -> Any: ...
def generate_private_key(curve, backend = ...) -> Any: ...
def get_curve_for_oid(oid) -> Any: ...
