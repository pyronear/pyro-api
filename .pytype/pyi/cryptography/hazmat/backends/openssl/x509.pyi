# (generated with --quick)

import __future__
import cryptography.exceptions
import cryptography.x509.name
from typing import Any, Type

UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_ASN1Type: Type[cryptography.x509.name._ASN1Type]
_Certificate: Any
_CertificateRevocationList: Any
_CertificateSigningRequest: Any
_RevokedCertificate: Any
_SignedCertificateTimestamp: Any
absolute_import: __future__._Feature
datetime: module
division: __future__._Feature
dsa: module
ec: module
hashes: module
operator: module
print_function: __future__._Feature
rsa: module
serialization: module
utils: module
x509: module

def _asn1_integer_to_int(backend, asn1_int) -> Any: ...
def _asn1_string_to_bytes(backend, asn1_string) -> Any: ...
def _decode_x509_name(backend, x509_name) -> Any: ...
def _encode_asn1_int_gc(backend, x) -> Any: ...
def _obj2txt(backend, obj) -> Any: ...
def _parse_asn1_time(backend, asn1_time) -> Any: ...
def _txt2obj_gc(backend, name) -> Any: ...
