# (generated with --quick)

import __future__
import cryptography.hazmat._der
import cryptography.hazmat.primitives.asymmetric.ec
import cryptography.hazmat.primitives.asymmetric.rsa
import cryptography.x509.certificate_transparency
import cryptography.x509.general_name
import cryptography.x509.name
import cryptography.x509.oid
import enum
from typing import Any, Callable, Dict, Tuple, Type, Union

AuthorityInformationAccess: Any
AuthorityKeyIdentifier: Any
BIT_STRING: int
BasicConstraints: Any
CRLDistributionPoints: Any
CRLEntryExtensionOID: Type[cryptography.x509.oid.CRLEntryExtensionOID]
CRLNumber: Any
CRLReason: Any
CertificateIssuer: Any
CertificatePolicies: Any
DERReader: Type[cryptography.hazmat._der.DERReader]
DeltaCRLIndicator: Any
EllipticCurvePublicKey: Type[cryptography.hazmat.primitives.asymmetric.ec.EllipticCurvePublicKey]
Enum: Type[enum.Enum]
ExtendedKeyUsage: Any
ExtensionOID: Type[cryptography.x509.oid.ExtensionOID]
FreshestCRL: Any
GeneralName: Type[cryptography.x509.general_name.GeneralName]
IPAddress: Any
InhibitAnyPolicy: Any
InvalidityDate: Any
IssuerAlternativeName: Any
IssuingDistributionPoint: Any
KeyUsage: Any
NameConstraints: Any
OBJECT_IDENTIFIER: int
OCSPExtensionOID: Type[cryptography.x509.oid.OCSPExtensionOID]
OCSPNoCheck: Any
OCSPNonce: Any
ObjectIdentifier: Any
OtherName: Any
PolicyConstraints: Any
PrecertPoison: Any
PrecertificateSignedCertificateTimestamps: Any
RSAPublicKey: Type[cryptography.hazmat.primitives.asymmetric.rsa.RSAPublicKey]
RelativeDistinguishedName: Type[cryptography.x509.name.RelativeDistinguishedName]
SEQUENCE: int
SignedCertificateTimestamp: Type[cryptography.x509.certificate_transparency.SignedCertificateTimestamp]
SignedCertificateTimestamps: Any
SubjectAlternativeName: Any
SubjectInformationAccess: Any
SubjectKeyIdentifier: Any
TLSFeature: Any
UnrecognizedExtension: Any
_TLS_FEATURE_TYPE_TO_ENUM: Dict[Any, TLSFeatureType]
abc: module
absolute_import: __future__._Feature
constant_time: module
datetime: module
division: __future__._Feature
hashlib: module
ipaddress: module
print_function: __future__._Feature
serialization: module
six: module
utils: module

class AccessDescription:
    _access_location: Any
    _access_method: Any
    access_location: Any
    access_method: Any
    def __eq__(self, other) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, access_method, access_location) -> None: ...
    def __ne__(self, other) -> bool: ...
    def __repr__(self) -> str: ...

class DistributionPoint:
    _crl_issuer: Any
    _full_name: Any
    _reasons: Any
    _relative_name: Any
    crl_issuer: Any
    full_name: Any
    reasons: Any
    relative_name: Any
    def __eq__(self, other) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, full_name, relative_name, reasons, crl_issuer) -> None: ...
    def __ne__(self, other) -> bool: ...
    def __repr__(self) -> str: ...

class DuplicateExtension(Exception):
    oid: Any
    def __init__(self, msg, oid) -> None: ...

class Extension:
    _critical: Any
    _oid: Any
    _value: Any
    critical: Any
    oid: Any
    value: Any
    def __eq__(self, other) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, oid, critical, value) -> None: ...
    def __ne__(self, other) -> bool: ...
    def __repr__(self) -> str: ...

class ExtensionNotFound(Exception):
    oid: Any
    def __init__(self, msg, oid) -> None: ...

class ExtensionType(metaclass=abc.ABCMeta):
    oid: Any

class Extensions:
    _extensions: Any
    def __getitem__(self, idx) -> Any: ...
    def __init__(self, extensions) -> None: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __repr__(self) -> str: ...
    def get_extension_for_class(self, extclass) -> Any: ...
    def get_extension_for_oid(self, oid) -> Any: ...

class GeneralNames:
    _general_names: list
    def __eq__(self, other) -> Union[NotImplementedType, bool]: ...
    def __getitem__(self, idx) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, general_names) -> None: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __ne__(self, other) -> bool: ...
    def __repr__(self) -> str: ...
    def get_values_for_type(self, type) -> list: ...

class NoticeReference:
    _notice_numbers: list
    _organization: Any
    notice_numbers: Any
    organization: Any
    def __eq__(self, other) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, organization, notice_numbers) -> None: ...
    def __ne__(self, other) -> bool: ...
    def __repr__(self) -> str: ...

class PolicyInformation:
    _policy_identifier: Any
    _policy_qualifiers: Any
    policy_identifier: Any
    policy_qualifiers: Any
    def __eq__(self, other) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, policy_identifier, policy_qualifiers) -> None: ...
    def __ne__(self, other) -> bool: ...
    def __repr__(self) -> str: ...

class ReasonFlags(enum.Enum):
    aa_compromise: str
    affiliation_changed: str
    ca_compromise: str
    certificate_hold: str
    cessation_of_operation: str
    key_compromise: str
    privilege_withdrawn: str
    remove_from_crl: str
    superseded: str
    unspecified: str

class TLSFeatureType(enum.Enum):
    status_request: int
    status_request_v2: int

class UserNotice:
    _explicit_text: Any
    _notice_reference: Any
    explicit_text: Any
    notice_reference: Any
    def __eq__(self, other) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, notice_reference, explicit_text) -> None: ...
    def __ne__(self, other) -> bool: ...
    def __repr__(self) -> str: ...

def _key_identifier_from_public_key(public_key) -> bytes: ...
def _make_sequence_methods(field_name) -> Tuple[Callable[[Any], Any], Callable[[Any], Any], Callable[[Any, Any], Any]]: ...
