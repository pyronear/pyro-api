# (generated with --quick)

import __future__
import cryptography.hazmat._oid
from typing import Any, Dict, Type

ObjectIdentifier: Type[cryptography.hazmat._oid.ObjectIdentifier]
_OID_NAMES: Dict[Any, str]
_SIG_OIDS_TO_HASH: Dict[cryptography.hazmat._oid.ObjectIdentifier, Any]
absolute_import: __future__._Feature
division: __future__._Feature
hashes: module
print_function: __future__._Feature

class AttributeOID:
    CHALLENGE_PASSWORD: cryptography.hazmat._oid.ObjectIdentifier
    UNSTRUCTURED_NAME: cryptography.hazmat._oid.ObjectIdentifier

class AuthorityInformationAccessOID:
    CA_ISSUERS: cryptography.hazmat._oid.ObjectIdentifier
    OCSP: cryptography.hazmat._oid.ObjectIdentifier

class CRLEntryExtensionOID:
    CERTIFICATE_ISSUER: cryptography.hazmat._oid.ObjectIdentifier
    CRL_REASON: cryptography.hazmat._oid.ObjectIdentifier
    INVALIDITY_DATE: cryptography.hazmat._oid.ObjectIdentifier

class CertificatePoliciesOID:
    ANY_POLICY: cryptography.hazmat._oid.ObjectIdentifier
    CPS_QUALIFIER: cryptography.hazmat._oid.ObjectIdentifier
    CPS_USER_NOTICE: cryptography.hazmat._oid.ObjectIdentifier

class ExtendedKeyUsageOID:
    ANY_EXTENDED_KEY_USAGE: cryptography.hazmat._oid.ObjectIdentifier
    CLIENT_AUTH: cryptography.hazmat._oid.ObjectIdentifier
    CODE_SIGNING: cryptography.hazmat._oid.ObjectIdentifier
    EMAIL_PROTECTION: cryptography.hazmat._oid.ObjectIdentifier
    OCSP_SIGNING: cryptography.hazmat._oid.ObjectIdentifier
    SERVER_AUTH: cryptography.hazmat._oid.ObjectIdentifier
    TIME_STAMPING: cryptography.hazmat._oid.ObjectIdentifier

class ExtensionOID:
    AUTHORITY_INFORMATION_ACCESS: cryptography.hazmat._oid.ObjectIdentifier
    AUTHORITY_KEY_IDENTIFIER: cryptography.hazmat._oid.ObjectIdentifier
    BASIC_CONSTRAINTS: cryptography.hazmat._oid.ObjectIdentifier
    CERTIFICATE_POLICIES: cryptography.hazmat._oid.ObjectIdentifier
    CRL_DISTRIBUTION_POINTS: cryptography.hazmat._oid.ObjectIdentifier
    CRL_NUMBER: cryptography.hazmat._oid.ObjectIdentifier
    DELTA_CRL_INDICATOR: cryptography.hazmat._oid.ObjectIdentifier
    EXTENDED_KEY_USAGE: cryptography.hazmat._oid.ObjectIdentifier
    FRESHEST_CRL: cryptography.hazmat._oid.ObjectIdentifier
    INHIBIT_ANY_POLICY: cryptography.hazmat._oid.ObjectIdentifier
    ISSUER_ALTERNATIVE_NAME: cryptography.hazmat._oid.ObjectIdentifier
    ISSUING_DISTRIBUTION_POINT: cryptography.hazmat._oid.ObjectIdentifier
    KEY_USAGE: cryptography.hazmat._oid.ObjectIdentifier
    NAME_CONSTRAINTS: cryptography.hazmat._oid.ObjectIdentifier
    OCSP_NO_CHECK: cryptography.hazmat._oid.ObjectIdentifier
    POLICY_CONSTRAINTS: cryptography.hazmat._oid.ObjectIdentifier
    POLICY_MAPPINGS: cryptography.hazmat._oid.ObjectIdentifier
    PRECERT_POISON: cryptography.hazmat._oid.ObjectIdentifier
    PRECERT_SIGNED_CERTIFICATE_TIMESTAMPS: cryptography.hazmat._oid.ObjectIdentifier
    SIGNED_CERTIFICATE_TIMESTAMPS: cryptography.hazmat._oid.ObjectIdentifier
    SUBJECT_ALTERNATIVE_NAME: cryptography.hazmat._oid.ObjectIdentifier
    SUBJECT_DIRECTORY_ATTRIBUTES: cryptography.hazmat._oid.ObjectIdentifier
    SUBJECT_INFORMATION_ACCESS: cryptography.hazmat._oid.ObjectIdentifier
    SUBJECT_KEY_IDENTIFIER: cryptography.hazmat._oid.ObjectIdentifier
    TLS_FEATURE: cryptography.hazmat._oid.ObjectIdentifier

class NameOID:
    BUSINESS_CATEGORY: cryptography.hazmat._oid.ObjectIdentifier
    COMMON_NAME: cryptography.hazmat._oid.ObjectIdentifier
    COUNTRY_NAME: cryptography.hazmat._oid.ObjectIdentifier
    DN_QUALIFIER: cryptography.hazmat._oid.ObjectIdentifier
    DOMAIN_COMPONENT: cryptography.hazmat._oid.ObjectIdentifier
    EMAIL_ADDRESS: cryptography.hazmat._oid.ObjectIdentifier
    GENERATION_QUALIFIER: cryptography.hazmat._oid.ObjectIdentifier
    GIVEN_NAME: cryptography.hazmat._oid.ObjectIdentifier
    INN: cryptography.hazmat._oid.ObjectIdentifier
    JURISDICTION_COUNTRY_NAME: cryptography.hazmat._oid.ObjectIdentifier
    JURISDICTION_LOCALITY_NAME: cryptography.hazmat._oid.ObjectIdentifier
    JURISDICTION_STATE_OR_PROVINCE_NAME: cryptography.hazmat._oid.ObjectIdentifier
    LOCALITY_NAME: cryptography.hazmat._oid.ObjectIdentifier
    OGRN: cryptography.hazmat._oid.ObjectIdentifier
    ORGANIZATIONAL_UNIT_NAME: cryptography.hazmat._oid.ObjectIdentifier
    ORGANIZATION_NAME: cryptography.hazmat._oid.ObjectIdentifier
    POSTAL_ADDRESS: cryptography.hazmat._oid.ObjectIdentifier
    POSTAL_CODE: cryptography.hazmat._oid.ObjectIdentifier
    PSEUDONYM: cryptography.hazmat._oid.ObjectIdentifier
    SERIAL_NUMBER: cryptography.hazmat._oid.ObjectIdentifier
    SNILS: cryptography.hazmat._oid.ObjectIdentifier
    STATE_OR_PROVINCE_NAME: cryptography.hazmat._oid.ObjectIdentifier
    STREET_ADDRESS: cryptography.hazmat._oid.ObjectIdentifier
    SURNAME: cryptography.hazmat._oid.ObjectIdentifier
    TITLE: cryptography.hazmat._oid.ObjectIdentifier
    UNSTRUCTURED_NAME: cryptography.hazmat._oid.ObjectIdentifier
    USER_ID: cryptography.hazmat._oid.ObjectIdentifier
    X500_UNIQUE_IDENTIFIER: cryptography.hazmat._oid.ObjectIdentifier

class OCSPExtensionOID:
    NONCE: cryptography.hazmat._oid.ObjectIdentifier

class SignatureAlgorithmOID:
    DSA_WITH_SHA1: cryptography.hazmat._oid.ObjectIdentifier
    DSA_WITH_SHA224: cryptography.hazmat._oid.ObjectIdentifier
    DSA_WITH_SHA256: cryptography.hazmat._oid.ObjectIdentifier
    ECDSA_WITH_SHA1: cryptography.hazmat._oid.ObjectIdentifier
    ECDSA_WITH_SHA224: cryptography.hazmat._oid.ObjectIdentifier
    ECDSA_WITH_SHA256: cryptography.hazmat._oid.ObjectIdentifier
    ECDSA_WITH_SHA384: cryptography.hazmat._oid.ObjectIdentifier
    ECDSA_WITH_SHA512: cryptography.hazmat._oid.ObjectIdentifier
    ED25519: cryptography.hazmat._oid.ObjectIdentifier
    ED448: cryptography.hazmat._oid.ObjectIdentifier
    GOSTR3410_2012_WITH_3411_2012_256: cryptography.hazmat._oid.ObjectIdentifier
    GOSTR3410_2012_WITH_3411_2012_512: cryptography.hazmat._oid.ObjectIdentifier
    GOSTR3411_94_WITH_3410_2001: cryptography.hazmat._oid.ObjectIdentifier
    RSASSA_PSS: cryptography.hazmat._oid.ObjectIdentifier
    RSA_WITH_MD5: cryptography.hazmat._oid.ObjectIdentifier
    RSA_WITH_SHA1: cryptography.hazmat._oid.ObjectIdentifier
    RSA_WITH_SHA224: cryptography.hazmat._oid.ObjectIdentifier
    RSA_WITH_SHA256: cryptography.hazmat._oid.ObjectIdentifier
    RSA_WITH_SHA384: cryptography.hazmat._oid.ObjectIdentifier
    RSA_WITH_SHA512: cryptography.hazmat._oid.ObjectIdentifier
    _RSA_WITH_SHA1: cryptography.hazmat._oid.ObjectIdentifier

class SubjectInformationAccessOID:
    CA_REPOSITORY: cryptography.hazmat._oid.ObjectIdentifier
