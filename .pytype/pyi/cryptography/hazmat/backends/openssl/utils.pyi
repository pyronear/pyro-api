# (generated with --quick)

import __future__
import cryptography.hazmat.primitives.asymmetric.utils
from typing import Any, Tuple, Type

Prehashed: Type[cryptography.hazmat.primitives.asymmetric.utils.Prehashed]
absolute_import: __future__._Feature
division: __future__._Feature
hashes: module
print_function: __future__._Feature
utils: module
warnings: module

def _calculate_digest_and_algorithm(backend, data, algorithm) -> Tuple[Any, Any]: ...
def _check_not_prehashed(signature_algorithm) -> None: ...
def _evp_pkey_derive(backend, evp_pkey, peer_public_key) -> Any: ...
def _warn_sign_verify_deprecated() -> None: ...
