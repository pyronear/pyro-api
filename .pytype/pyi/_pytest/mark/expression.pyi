# (generated with --quick)

import _ast
from typing import Any, Callable, Iterator, List, Mapping, NoReturn, Optional, Sequence, TypeVar

IDENT_PREFIX: str
TYPE_CHECKING: Any
__all__: List[str]
ast: module
attr: module
enum: module
re: module
types: module

_TExpression = TypeVar('_TExpression', bound=Expression)

class Expression:
    __slots__ = ["code"]
    __doc__: str
    code: types.CodeType
    def __init__(self, code: types.CodeType) -> None: ...
    @classmethod
    def compile(self: _TExpression, input: str) -> _TExpression: ...
    def evaluate(self, matcher: Callable[[str], bool]) -> bool: ...

class MatcherAdapter(Mapping[str, bool]):
    __doc__: str
    matcher: Callable[[str], bool]
    def __getitem__(self, key: str) -> bool: ...
    def __init__(self, matcher: Callable[[str], bool]) -> None: ...
    def __iter__(self) -> Iterator[str]: ...
    def __len__(self) -> int: ...

class ParseError(Exception):
    __doc__: str
    column: int
    message: str
    def __init__(self, column: int, message: str) -> None: ...
    def __str__(self) -> str: ...

class Scanner:
    __slots__ = ["current", "tokens"]
    current: Any
    tokens: Any
    def __init__(self, input: str) -> None: ...
    def accept(self, type: TokenType, *, reject: bool = ...) -> Optional[Token]: ...
    def lex(self, input: str) -> Iterator[Token]: ...
    def reject(self, expected: Sequence[TokenType]) -> NoReturn: ...

class Token:
    pos: int
    type: TokenType
    value: str
    def __init__(self, type: TokenType, value: str, pos: int) -> None: ...

class TokenType(enum.Enum):
    AND: str
    EOF: str
    IDENT: str
    LPAREN: str
    NOT: str
    OR: str
    RPAREN: str

def and_expr(s: Scanner) -> _ast.expr: ...
def expr(s: Scanner) -> _ast.expr: ...
def expression(s: Scanner) -> _ast.Expression: ...
def not_expr(s: Scanner) -> _ast.expr: ...
