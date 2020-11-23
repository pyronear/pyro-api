# (generated with --quick)

import ipaddress
import pydantic.fields
import pydantic.main
import pydantic.utils
from typing import Any, Callable, Dict, Generator, List, Optional, Pattern, Set, Tuple, Type, Union

CallableGenerator = Generator[Callable, None, None]

AnyCallable: Type[Callable]
BaseConfig: Type[pydantic.main.BaseConfig]
IPv4Address: Type[ipaddress.IPv4Address]
IPv4Interface: Type[ipaddress.IPv4Interface]
IPv4Network: Type[ipaddress.IPv4Network]
IPv6Address: Type[ipaddress.IPv6Address]
IPv6Interface: Type[ipaddress.IPv6Interface]
IPv6Network: Type[ipaddress.IPv6Network]
ModelField: Type[pydantic.fields.ModelField]
NetworkType: Type[Union[bytes, int, str, Tuple[Union[bytes, int, str], Union[int, str]]]]
Representation: Type[pydantic.utils.Representation]
_BaseAddress: Type[ipaddress._BaseAddress]
_BaseNetwork: Type[ipaddress._BaseNetwork]
__all__: List[str]
_ascii_domain_regex_cache: None
_int_domain_regex_cache: None
_url_regex_cache: None
email_validator: Any
errors: module
pretty_email_regex: Pattern[str]
re: module

class AnyHttpUrl(AnyUrl):
    allowed_schemes: Set[str]
    fragment: Any
    host: str
    host_type: str
    password: Any
    path: Any
    port: Any
    query: Any
    scheme: str
    tld: Any
    user: Any

class AnyUrl(str):
    __slots__ = ["fragment", "host", "host_type", "password", "path", "port", "query", "scheme", "tld", "user"]
    allowed_schemes: Optional[Set[str]]
    fragment: Any
    host: str
    host_type: str
    max_length: int
    min_length: int
    password: Any
    path: Any
    port: Any
    query: Any
    scheme: str
    strip_whitespace: bool
    tld: Any
    tld_required: bool
    user: Any
    user_required: bool
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    def __init__(self, url: str, *, scheme: str, user: Optional[str] = ..., password: Optional[str] = ..., host: str, tld: Optional[str] = ..., host_type: str = ..., port: Optional[str] = ..., path: Optional[str] = ..., query: Optional[str] = ..., fragment: Optional[str] = ...) -> None: ...
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None: ...
    def __new__(cls, url: Optional[str], **kwargs) -> Any: ...
    def __repr__(self) -> str: ...
    @classmethod
    def build(cls, *, scheme: str, user: Optional[str] = ..., password: Optional[str] = ..., host: str, port: Optional[str] = ..., path: Optional[str] = ..., query: Optional[str] = ..., fragment: Optional[str] = ..., **kwargs: str) -> str: ...
    @classmethod
    def validate(cls, value, field: pydantic.fields.ModelField, config: pydantic.main.BaseConfig) -> AnyUrl: ...
    @classmethod
    def validate_host(cls, parts: Dict[str, str]) -> Tuple[str, Optional[str], str, bool]: ...

class EmailStr(str):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None: ...
    @classmethod
    def validate(cls, value: str) -> str: ...

class HttpUrl(AnyUrl):
    allowed_schemes: Set[str]
    fragment: Any
    host: str
    host_type: str
    max_length: int
    password: Any
    path: Any
    port: Any
    query: Any
    scheme: str
    tld: Any
    tld_required: bool
    user: Any

class IPvAnyAddress(ipaddress._BaseAddress):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None: ...
    @classmethod
    def validate(cls, value: Union[bytes, int, str]) -> Union[ipaddress.IPv4Address, ipaddress.IPv6Address]: ...

class IPvAnyInterface(ipaddress._BaseAddress):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None: ...
    @classmethod
    def validate(cls, value: Union[bytes, int, str, Tuple[Union[bytes, int, str], Union[int, str]]]) -> Union[ipaddress.IPv4Interface, ipaddress.IPv6Interface]: ...

class IPvAnyNetwork(ipaddress._BaseNetwork):
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None: ...
    @classmethod
    def validate(cls, value: Union[bytes, int, str, Tuple[Union[bytes, int, str], Union[int, str]]]) -> Union[ipaddress.IPv4Network, ipaddress.IPv6Network]: ...

class NameEmail(pydantic.utils.Representation):
    __slots__ = ["email", "name"]
    email: str
    name: str
    def __eq__(self, other) -> bool: ...
    @classmethod
    def __get_validators__(cls) -> Generator[Callable, None, None]: ...
    def __init__(self, name: str, email: str) -> None: ...
    @classmethod
    def __modify_schema__(cls, field_schema: Dict[str, Any]) -> None: ...
    def __str__(self) -> str: ...
    @classmethod
    def validate(cls, value) -> NameEmail: ...

class PostgresDsn(AnyUrl):
    allowed_schemes: Set[str]
    fragment: Any
    host: str
    host_type: str
    password: Any
    path: Any
    port: Any
    query: Any
    scheme: str
    tld: Any
    user: Any
    user_required: bool

class RedisDsn(AnyUrl):
    allowed_schemes: Set[str]
    fragment: Any
    host: str
    host_type: str
    password: Any
    path: Any
    port: Any
    query: Any
    scheme: str
    tld: Any
    user: Any

def ascii_domain_regex() -> Pattern[str]: ...
def constr_length_validator(v: Union[bytes, str], field, config) -> Union[bytes, str]: ...
def import_email_validator() -> None: ...
def int_domain_regex() -> Pattern[str]: ...
def str_validator(v) -> str: ...
def stricturl(*, strip_whitespace: bool = ..., min_length: int = ..., max_length: int = ..., tld_required: bool = ..., allowed_schemes: Optional[Set[str]] = ...) -> Type[AnyUrl]: ...
def update_not_none(mapping: dict, **update) -> None: ...
def url_regex() -> Pattern[str]: ...
def validate_email(value: str) -> Tuple[str, str]: ...
