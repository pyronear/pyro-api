# (generated with --quick)

import jose.backends.cryptography_backend
import jose.backends.ecdsa_backend
import jose.backends.pycrypto_backend
import jose.backends.rsa_backend
from typing import Type, Union

ECKey: Type[Union[jose.backends.cryptography_backend.CryptographyECKey, jose.backends.ecdsa_backend.ECDSAECKey]]
RSAKey: Type[Union[jose.backends.cryptography_backend.CryptographyRSAKey, jose.backends.pycrypto_backend.RSAKey, jose.backends.rsa_backend.RSAKey]]
