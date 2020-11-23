# (generated with --quick)

import __future__
import cryptography.exceptions
import cryptography.hazmat.primitives.asymmetric
from typing import Any, Tuple, Type, TypeVar, Union

AsymmetricSignatureContext: Type[cryptography.hazmat.primitives.asymmetric.AsymmetricSignatureContext]
AsymmetricVerificationContext: Type[cryptography.hazmat.primitives.asymmetric.AsymmetricVerificationContext]
InvalidSignature: Type[cryptography.exceptions.InvalidSignature]
UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_ECDSASignatureContext: Any
_ECDSAVerificationContext: Any
_EllipticCurvePrivateKey: Any
_EllipticCurvePublicKey: Any
_Reasons: Type[cryptography.exceptions._Reasons]
absolute_import: __future__._Feature
division: __future__._Feature
ec: module
hashes: module
print_function: __future__._Feature
serialization: module
utils: module

_T1 = TypeVar('_T1')

def _calculate_digest_and_algorithm(backend, data: _T1, algorithm) -> Tuple[Union[bytes, _T1], Any]: ...
def _check_not_prehashed(signature_algorithm) -> None: ...
def _check_signature_algorithm(signature_algorithm) -> None: ...
def _ec_key_curve_sn(backend, ec_key) -> Any: ...
def _ecdsa_sig_sign(backend, private_key, data) -> Any: ...
def _ecdsa_sig_verify(backend, public_key, signature, data) -> None: ...
def _mark_asn1_named_ec_curve(backend, ec_cdata) -> None: ...
def _sn_to_elliptic_curve(backend, sn) -> Any: ...
def _warn_sign_verify_deprecated() -> None: ...
