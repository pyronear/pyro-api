# (generated with --quick)

import pyasn1.type.namedtype
import pyasn1.type.univ
from typing import Any

RSA_ENCRYPTION_ASN1_OID: str
decoder: module
encoder: module
namedtype: module
univ: module

class PKCS8PrivateKey(pyasn1.type.univ.Sequence):
    __doc__: str
    componentType: pyasn1.type.namedtype.NamedTypes

class PublicKeyInfo(pyasn1.type.univ.Sequence):
    __doc__: str
    componentType: pyasn1.type.namedtype.NamedTypes

class RsaAlgorithmIdentifier(pyasn1.type.univ.Sequence):
    __doc__: str
    componentType: pyasn1.type.namedtype.NamedTypes

def rsa_private_key_pkcs1_to_pkcs8(pkcs1_key) -> Any: ...
def rsa_private_key_pkcs8_to_pkcs1(pkcs8_key) -> Any: ...
def rsa_public_key_pkcs1_to_pkcs8(pkcs1_key) -> Any: ...
def rsa_public_key_pkcs8_to_pkcs1(pkcs8_key) -> Any: ...
