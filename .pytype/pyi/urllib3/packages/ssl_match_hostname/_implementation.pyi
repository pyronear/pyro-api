# (generated with --quick)

from typing import Any, Optional, TypeVar

__version__: str
ipaddress: Optional[module]
re: module
sys: module

_T0 = TypeVar('_T0')

class CertificateError(ValueError): ...

def _dnsname_match(dn, hostname, max_wildcards = ...) -> Any: ...
def _ipaddress_match(ipname, host_ip) -> Any: ...
def _to_unicode(obj: _T0) -> _T0: ...
def match_hostname(cert, hostname) -> None: ...
