# (generated with --quick)

import backports.ssl_match_hostname
import ssl
from typing import Any, Tuple, Type, Union
import urllib3.packages.ssl_match_hostname._implementation

CertificateError: Type[Union[backports.ssl_match_hostname.CertificateError, ssl.SSLCertVerificationError, urllib3.packages.ssl_match_hostname._implementation.CertificateError]]
__all__: Tuple[str, str]
sys: module

def match_hostname(cert, hostname) -> Any: ...
