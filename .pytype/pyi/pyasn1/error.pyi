# (generated with --quick)

class PyAsn1Error(Exception):
    __doc__: str

class PyAsn1UnicodeDecodeError(PyAsn1UnicodeError, UnicodeDecodeError):
    __doc__: str

class PyAsn1UnicodeEncodeError(PyAsn1UnicodeError, UnicodeEncodeError):
    __doc__: str

class PyAsn1UnicodeError(PyAsn1Error, UnicodeError):
    __doc__: str
    def __init__(self, message, unicode_error = ...) -> None: ...

class SubstrateUnderrunError(PyAsn1Error):
    __doc__: str

class ValueConstraintError(PyAsn1Error):
    __doc__: str
