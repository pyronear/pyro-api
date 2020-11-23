# (generated with --quick)

import pyasn1.type.namedtype
import pyasn1.type.univ

namedtype: module
tag: module
univ: module

class AsnPubKey(pyasn1.type.univ.Sequence):
    __doc__: str
    componentType: pyasn1.type.namedtype.NamedTypes

class OpenSSLPubKey(pyasn1.type.univ.Sequence):
    componentType: pyasn1.type.namedtype.NamedTypes

class PubKeyHeader(pyasn1.type.univ.Sequence):
    componentType: pyasn1.type.namedtype.NamedTypes
