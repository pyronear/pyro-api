# (generated with --quick)

import __future__
import cryptography.exceptions
import cryptography.hazmat.primitives.asymmetric
import cryptography.hazmat.primitives.asymmetric.padding
import cryptography.hazmat.primitives.asymmetric.rsa
from typing import Any, NoReturn, Tuple, Type, TypeVar, Union

AsymmetricPadding: Type[cryptography.hazmat.primitives.asymmetric.padding.AsymmetricPadding]
AsymmetricSignatureContext: Type[cryptography.hazmat.primitives.asymmetric.AsymmetricSignatureContext]
AsymmetricVerificationContext: Type[cryptography.hazmat.primitives.asymmetric.AsymmetricVerificationContext]
InvalidSignature: Type[cryptography.exceptions.InvalidSignature]
MGF1: Type[cryptography.hazmat.primitives.asymmetric.padding.MGF1]
OAEP: Any
PKCS1v15: Any
PSS: Any
RSAPrivateKeyWithSerialization: Type[cryptography.hazmat.primitives.asymmetric.rsa.RSAPrivateKeyWithSerialization]
RSAPublicKeyWithSerialization: Type[cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey]
UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_RSAPrivateKey: Any
_RSAPublicKey: Any
_RSASignatureContext: Any
_RSAVerificationContext: Any
_Reasons: Type[cryptography.exceptions._Reasons]
absolute_import: __future__._Feature
division: __future__._Feature
hashes: module
print_function: __future__._Feature
rsa: module
utils: module

_T1 = TypeVar('_T1')

def _calculate_digest_and_algorithm(backend, data: _T1, algorithm) -> Tuple[Union[bytes, _T1], Any]: ...
def _check_not_prehashed(signature_algorithm) -> None: ...
def _enc_dec_rsa(backend, key, data, padding) -> Any: ...
def _enc_dec_rsa_pkey_ctx(backend, key, data, padding_enum, padding) -> Any: ...
def _get_rsa_pss_salt_length(pss, key, hash_algorithm) -> Any: ...
def _handle_rsa_enc_dec_error(backend, key) -> NoReturn: ...
def _rsa_sig_determine_padding(backend, key, padding, algorithm) -> Any: ...
def _rsa_sig_setup(backend, padding, algorithm, key, data, init_func) -> Any: ...
def _rsa_sig_sign(backend, padding, algorithm, private_key, data) -> Any: ...
def _rsa_sig_verify(backend, padding, algorithm, public_key, signature, data) -> None: ...
def _warn_sign_verify_deprecated() -> None: ...
def calculate_max_pss_salt_length(key, hash_algorithm) -> Any: ...
