# (generated with --quick)

import __future__
import cryptography.exceptions
import cryptography.x509.ocsp
import datetime
from typing import Any, Callable, Dict, Type

OCSPCertStatus: Type[cryptography.x509.ocsp.OCSPCertStatus]
OCSPRequest: Type[cryptography.x509.ocsp.OCSPRequest]
OCSPResponse: Type[cryptography.x509.ocsp.OCSPResponse]
OCSPResponseStatus: Type[cryptography.x509.ocsp.OCSPResponseStatus]
UnsupportedAlgorithm: Type[cryptography.exceptions.UnsupportedAlgorithm]
_CERT_STATUS_TO_ENUM: Dict[Any, cryptography.x509.ocsp.OCSPCertStatus]
_CRL_ENTRY_REASON_CODE_TO_ENUM: Dict[int, Any]
_Certificate: Any
_OCSPRequest: Any
_OCSPResponse: Any
_OIDS_TO_HASH: Dict[str, Any]
_RESPONSE_STATUS_TO_ENUM: Dict[Any, cryptography.x509.ocsp.OCSPResponseStatus]
absolute_import: __future__._Feature
division: __future__._Feature
functools: module
print_function: __future__._Feature
serialization: module
utils: module
x509: module

def _asn1_integer_to_int(backend, asn1_int) -> Any: ...
def _asn1_string_to_bytes(backend, asn1_string) -> Any: ...
def _decode_x509_name(backend, x509_name) -> Any: ...
def _hash_algorithm(backend, cert_id) -> Any: ...
def _issuer_key_hash(backend, cert_id) -> Any: ...
def _issuer_name_hash(backend, cert_id) -> Any: ...
def _obj2txt(backend, obj) -> Any: ...
def _parse_asn1_generalized_time(backend, generalized_time) -> datetime.datetime: ...
def _requires_successful_response(func) -> Callable: ...
def _serial_number(backend, cert_id) -> Any: ...
