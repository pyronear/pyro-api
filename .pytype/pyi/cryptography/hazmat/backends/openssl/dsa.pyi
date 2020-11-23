# (generated with --quick)

import __future__
import cryptography.exceptions
import cryptography.hazmat.primitives.asymmetric
from typing import Any, Tuple, Type, TypeVar, Union

AsymmetricSignatureContext: Type[cryptography.hazmat.primitives.asymmetric.AsymmetricSignatureContext]
AsymmetricVerificationContext: Type[cryptography.hazmat.primitives.asymmetric.AsymmetricVerificationContext]
InvalidSignature: Type[cryptography.exceptions.InvalidSignature]
_DSAParameters: Any
_DSAPrivateKey: Any
_DSAPublicKey: Any
_DSASignatureContext: Any
_DSAVerificationContext: Any
absolute_import: __future__._Feature
division: __future__._Feature
dsa: module
hashes: module
print_function: __future__._Feature
utils: module

_T1 = TypeVar('_T1')

def _calculate_digest_and_algorithm(backend, data: _T1, algorithm) -> Tuple[Union[bytes, _T1], Any]: ...
def _check_not_prehashed(signature_algorithm) -> None: ...
def _dsa_sig_sign(backend, private_key, data) -> Any: ...
def _dsa_sig_verify(backend, public_key, signature, data) -> None: ...
def _warn_sign_verify_deprecated() -> None: ...
