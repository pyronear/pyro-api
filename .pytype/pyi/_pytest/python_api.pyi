# (generated with --quick)

import _pytest.outcomes
import decimal
import numbers
import types
import typing
from typing import Any, Callable, Generator, Iterator, NoReturn, Optional, Tuple, Type, TypeVar, Union

Decimal: Type[decimal.Decimal]
Iterable: Type[typing.Iterable]
Mapping: Type[typing.Mapping]
Number: Type[numbers.Number]
RaisesContext: Any
STRING_TYPES: Tuple[Type[bytes], Type[str]]
Sized: Type[typing.Sized]
TYPE_CHECKING: Any
TracebackType: Type[types.TracebackType]
_pytest: module
fail: _pytest.outcomes._WithException[Callable, Type[_pytest.outcomes.Failed]]
final: Any
math: module
overload: Any
pprint: module

_E = TypeVar('_E', bound=BaseException)
_T0 = TypeVar('_T0')

class ApproxBase:
    __array_priority__: int
    __array_ufunc__: None
    __doc__: str
    __hash__: None
    abs: Any
    expected: Any
    nan_ok: bool
    rel: Any
    def __eq__(self, actual) -> bool: ...
    def __init__(self, expected, rel = ..., abs = ..., nan_ok: bool = ...) -> None: ...
    def __ne__(self, actual) -> bool: ...
    def __repr__(self) -> str: ...
    def _approx_scalar(self, x) -> ApproxScalar: ...
    def _check_type(self) -> None: ...
    def _yield_comparisons(self, actual) -> NoReturn: ...

class ApproxDecimal(ApproxScalar):
    DEFAULT_ABSOLUTE_TOLERANCE: decimal.Decimal
    DEFAULT_RELATIVE_TOLERANCE: decimal.Decimal
    __doc__: str
    abs: Any
    expected: Any
    nan_ok: bool
    rel: Any

class ApproxMapping(ApproxBase):
    __doc__: str
    abs: Any
    expected: Any
    nan_ok: bool
    rel: Any
    def __eq__(self, actual) -> bool: ...
    def __repr__(self) -> str: ...
    def _check_type(self) -> None: ...
    def _yield_comparisons(self, actual) -> Generator[Tuple[Any, Any], Any, None]: ...

class ApproxNumpy(ApproxBase):
    __doc__: str
    abs: Any
    expected: Any
    nan_ok: bool
    rel: Any
    def __eq__(self, actual) -> bool: ...
    def __repr__(self) -> str: ...
    def _yield_comparisons(self, actual: _T0) -> Generator[Tuple[Any, Any], Any, None]: ...

class ApproxScalar(ApproxBase):
    DEFAULT_ABSOLUTE_TOLERANCE: Union[float, decimal.Decimal]
    DEFAULT_RELATIVE_TOLERANCE: Union[float, decimal.Decimal]
    __doc__: str
    __hash__: None
    abs: Any
    expected: Any
    nan_ok: bool
    rel: Any
    tolerance: Any
    def __eq__(self, actual) -> bool: ...
    def __repr__(self) -> str: ...

class ApproxSequencelike(ApproxBase):
    __doc__: str
    abs: Any
    expected: Any
    nan_ok: bool
    rel: Any
    def __eq__(self, actual) -> bool: ...
    def __repr__(self) -> str: ...
    def _check_type(self) -> None: ...
    def _yield_comparisons(self, actual) -> Iterator[Tuple[Any, Any]]: ...

def _is_numpy_array(obj: object) -> bool: ...
def _non_numeric_type_error(value, at: Optional[str]) -> TypeError: ...
def _recursive_list_map(f, x) -> Any: ...
def approx(expected, rel = ..., abs = ..., nan_ok: bool = ...) -> ApproxBase: ...
def raises(expected_exception: Union[Tuple[Type[_E], ...], Type[_E]], *args, **kwargs) -> Any: ...
