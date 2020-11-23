# (generated with --quick)

import decimal
import pathlib
from typing import Any, Callable, Dict, Set, Tuple, Type, Union

Decimal: Type[decimal.Decimal]
DictStrAny: Any
Path: Type[pathlib.Path]
__all__: Tuple[str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str, str]

class AnyStrMaxLengthError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, limit_value: int) -> None: ...

class AnyStrMinLengthError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, limit_value: int) -> None: ...

class ArbitraryTypeError(PydanticTypeError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, expected_arbitrary_type: type) -> None: ...

class BoolError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class BytesError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class CallableError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class ClassError(PydanticTypeError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class ColorError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class ConfigError(RuntimeError): ...

class DataclassTypeError(PydanticTypeError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class DateError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class DateTimeError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class DecimalError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class DecimalIsNotFiniteError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class DecimalMaxDigitsError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, max_digits: int) -> None: ...

class DecimalMaxPlacesError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, decimal_places: int) -> None: ...

class DecimalWholeDigitsError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, whole_digits: int) -> None: ...

class DictError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class DurationError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class EmailError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class EnumError(PydanticTypeError):
    __dict__: Dict[str, Any]
    def __str__(self) -> str: ...

class ExtraError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class FloatError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class FrozenSetError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class HashableError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPv4AddressError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPv4InterfaceError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPv4NetworkError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPv6AddressError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPv6InterfaceError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPv6NetworkError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPvAnyAddressError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPvAnyInterfaceError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IPvAnyNetworkError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class IntegerError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class InvalidByteSize(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class InvalidByteSizeUnit(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class InvalidLengthForBrand(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class IterableError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class JsonError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class JsonTypeError(PydanticTypeError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class ListError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class ListMaxLengthError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, limit_value: int) -> None: ...

class ListMinLengthError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, limit_value: int) -> None: ...

class LuhnValidationError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class MissingError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class NoneIsAllowedError(PydanticTypeError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class NoneIsNotAllowedError(PydanticTypeError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class NotDigitError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class NumberNotGeError(_NumberBoundError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class NumberNotGtError(_NumberBoundError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class NumberNotLeError(_NumberBoundError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class NumberNotLtError(_NumberBoundError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class NumberNotMultipleError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, multiple_of: Union[float, decimal.Decimal]) -> None: ...

class PathError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class PathNotADirectoryError(_PathValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class PathNotAFileError(_PathValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class PathNotExistsError(_PathValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class PatternError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class PyObjectError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class PydanticErrorMixin:
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, **ctx) -> None: ...
    def __reduce__(self) -> Tuple[Callable[..., PydanticErrorMixin], Tuple[Type[PydanticErrorMixin], Any]]: ...
    def __str__(self) -> str: ...

class PydanticTypeError(PydanticErrorMixin, TypeError):
    __dict__: Dict[str, Any]

class PydanticValueError(PydanticErrorMixin, ValueError):
    __dict__: Dict[str, Any]

class SequenceError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class SetError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class SetMaxLengthError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, limit_value: int) -> None: ...

class SetMinLengthError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, limit_value: int) -> None: ...

class StrError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class StrRegexError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, pattern: str) -> None: ...

class StrictBoolError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class SubclassError(PydanticTypeError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, expected_class: type) -> None: ...

class TimeError(PydanticValueError):
    __dict__: Dict[str, Any]
    msg_template: str

class TupleError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class TupleLengthError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, actual_length: int, expected_length: int) -> None: ...

class UUIDError(PydanticTypeError):
    __dict__: Dict[str, Any]
    msg_template: str

class UUIDVersionError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, *, required_version: int) -> None: ...

class UrlError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str

class UrlExtraError(UrlError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class UrlHostError(UrlError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class UrlHostTldError(UrlError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class UrlPortError(UrlError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class UrlSchemeError(UrlError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class UrlSchemePermittedError(UrlError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str
    def __init__(self, allowed_schemes: Set[str]) -> None: ...

class UrlUserInfoError(UrlError):
    __dict__: Dict[str, Any]
    code: str
    msg_template: str

class WrongConstantError(PydanticValueError):
    __dict__: Dict[str, Any]
    code: str
    def __str__(self) -> str: ...

class _NumberBoundError(PydanticValueError):
    __dict__: Dict[str, Any]
    def __init__(self, *, limit_value: Union[float, decimal.Decimal]) -> None: ...

class _PathValueError(PydanticValueError):
    __dict__: Dict[str, Any]
    def __init__(self, *, path: pathlib.Path) -> None: ...

def cls_kwargs(cls: Type[PydanticErrorMixin], ctx) -> PydanticErrorMixin: ...
def display_as_type(v) -> str: ...
