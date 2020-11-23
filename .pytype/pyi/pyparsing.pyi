# (generated with --quick)

import _weakref
import contextlib
import typing
from typing import Any, Callable, Generator, Iterator, List, NoReturn, Pattern, Sequence, Set, Tuple, Type, TypeVar, Union

_L = Literal

Iterable: Type[typing.Iterable]
Mapping: Type[typing.Mapping]
MutableMapping: Type[typing.MutableMapping]
PY_3: bool
RLock: Any
SimpleNamespace: type
_MAX_INT: Any
_OrderedDict: Any
__all__: list
__author__: str
__builtin__: module
__compat__: Any
__diag__: Any
__versionTime__: str
__version__: str
_bslash: str
_charRange: Group
_commasepitem: Combine
_escapedHexChar: Regex
_escapedOctChar: Regex
_escapedPunc: Any
_generatorType: Type[generator]
_htmlEntityMap: typing.Dict[str, str]
_reBracketExpr: Any
_singleChar: MatchFirst
_ustr: Union[Callable[[Any], Any], Type[str]]
alphanums: str
alphas: str
alphas8bit: str
anyCloseTag: Any
anyOpenTag: Any
basestring: Type[str]
cStyleComment: Combine
collections: module
columnName: Combine
columnNameList: Group
columnSpec: Any
commaSeparatedList: And
commonHTMLEntity: Regex
copy: module
cppStyleComment: Combine
datetime: Type[datetime.datetime]
dblQuotedString: Combine
dblSlashComment: Regex
empty: Empty
filterfalse: Any
fname: str
fromToken: Any
hexnums: str
htmlComment: Regex
ident: Any
itertools: module
javaStyleComment: Combine
lineEnd: LineEnd
lineStart: LineStart
nums: str
opAssoc: Any
pprint: module
printables: str
punc8bit: str
pythonStyleComment: Regex
quotedString: Combine
range: Any
re: module
restOfLine: Regex
selectToken: Any
sglQuotedString: Combine
simpleSQL: Any
singleArgBuiltins: list
sre_constants: module
string: module
stringEnd: StringEnd
stringStart: StringStart
sys: module
system_version: Tuple[Union[int, str], ...]
tableName: Combine
tableNameList: Group
traceback: module
types: module
unicode: Type[str]
unicodeString: Combine
uuid: module
warnings: module
wkref: Type[_weakref.ReferenceType]

_T = TypeVar('_T')
_T0 = TypeVar('_T0')
_T1 = TypeVar('_T1')
_T2 = TypeVar('_T2')
_T5 = TypeVar('_T5')
_TAnd = TypeVar('_TAnd', bound=And)
_TCombine = TypeVar('_TCombine', bound=Combine)
_TEach = TypeVar('_TEach', bound=Each)
_TForward = TypeVar('_TForward', bound=Forward)
_TMatchFirst = TypeVar('_TMatchFirst', bound=MatchFirst)
_TOr = TypeVar('_TOr', bound=Or)
_TParseBaseException = TypeVar('_TParseBaseException', bound=ParseBaseException)
_TParseElementEnhance = TypeVar('_TParseElementEnhance', bound=ParseElementEnhance)
_TParseExpression = TypeVar('_TParseExpression', bound=ParseExpression)
_TParseResults = TypeVar('_TParseResults', bound=ParseResults)
_TParserElement = TypeVar('_TParserElement', bound=ParserElement)
_TSuppress = TypeVar('_TSuppress', bound=Suppress)
_T_MultipleMatch = TypeVar('_T_MultipleMatch', bound=_MultipleMatch)

class And(ParseExpression):
    _ErrorStop: type
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    exprs: Any
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: Any
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    tag: Any
    tag_body: SkipTo
    whiteChars: Any
    def __iadd__(self, other) -> Any: ...
    def __init__(self, exprs, savelist = ...) -> None: ...
    def __str__(self) -> Any: ...
    def checkRecursion(self, parseElementList) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...
    def streamline(self: _TAnd) -> _TAnd: ...

class CaselessKeyword(Keyword):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    caseless: bool
    caselessmatch: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    firstMatchChar: Any
    identChars: set
    ignoreExprs: List[nothing]
    keepTabs: bool
    match: Any
    matchLen: int
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: set
    def __init__(self, matchString, identChars = ...) -> None: ...

class CaselessLiteral(Literal):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    firstMatchChar: Any
    ignoreExprs: List[nothing]
    keepTabs: bool
    match: Any
    matchLen: int
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    returnString: Any
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: set
    def __init__(self, matchString) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...

class Char(_WordRegex):
    __doc__: str
    asKeyword: Any
    bodyChars: set
    bodyCharsOrig: Any
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    initChars: set
    initCharsOrig: Any
    keepTabs: bool
    maxLen: int
    maxSpecified: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    minLen: int
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: Pattern[str]
    reString: str
    re_match: Callable
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, charset, asKeyword = ..., excludeChars = ...) -> None: ...

class CharsNotIn(Token):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    maxLen: Any
    mayIndexError: bool
    mayReturnEmpty: Any
    minLen: Any
    modalResults: bool
    name: Any
    notChars: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: typing.Optional[str]
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, notChars, min = ..., max = ..., exact = ...) -> None: ...
    def __str__(self) -> Any: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...

class CloseMatch(Token):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    match_string: Any
    maxMismatches: Any
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, match_string, maxMismatches = ...) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[int, Any]: ...

class Combine(TokenConverter):
    __doc__: str
    adjacent: Any
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    joinString: Any
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    name: Any
    parseAction: list
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Any
    def __init__(self, expr, joinString = ..., adjacent = ...) -> None: ...
    def ignore(self: _TCombine, other) -> _TCombine: ...
    def postParse(self, instring, loc, tokenlist) -> Any: ...

class Dict(TokenConverter):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, expr) -> None: ...
    def postParse(self, instring, loc, tokenlist: _T2) -> Union[List[_T2], _T2]: ...

class Each(ParseExpression):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    exprs: list
    failAction: None
    ignoreExprs: List[nothing]
    initExprGroups: bool
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    multioptionals: Any
    multirequired: Any
    opt1map: dict
    optionals: Any
    parseAction: List[nothing]
    re: None
    required: Any
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, exprs, savelist = ...) -> None: ...
    def __str__(self) -> Any: ...
    def checkRecursion(self, parseElementList) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> NoReturn: ...
    def streamline(self: _TEach) -> _TEach: ...

class Empty(Token):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: set
    def __init__(self) -> None: ...

class FollowedBy(ParseElementEnhance):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: bool
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, expr) -> None: ...
    def parseImpl(self, instring, loc: _T1, doActions = ...) -> Tuple[_T1, Any]: ...

class Forward(ParseElementEnhance):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __ilshift__(self, other) -> Any: ...
    def __init__(self, other = ...) -> None: ...
    def __lshift__(self: _TForward, other) -> _TForward: ...
    def __str__(self) -> Any: ...
    def _setResultsName(self, name, listAllMatches = ...) -> Any: ...
    def copy(self) -> Any: ...
    def leaveWhitespace(self: _TForward) -> _TForward: ...
    def streamline(self: _TForward) -> _TForward: ...
    def validate(self, validateTrace = ...) -> None: ...

class GoToColumn(_PositionToken):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    col: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, colno) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...
    def preParse(self, instring, loc) -> Any: ...

class Group(TokenConverter):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: typing.Optional[str]
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Any
    def __init__(self, expr) -> None: ...
    def postParse(self, instring, loc, tokenlist: _T2) -> List[_T2]: ...

class Keyword(Token):
    DEFAULT_KEYWORD_CHARS: Any
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    caseless: Any
    caselessmatch: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    firstMatchChar: Any
    identChars: set
    ignoreExprs: List[nothing]
    keepTabs: bool
    match: Any
    matchLen: int
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: set
    def __init__(self, matchString, identChars = ..., caseless = ...) -> None: ...
    def copy(self) -> Any: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...
    @staticmethod
    def setDefaultKeywordChars(chars) -> None: ...

class LineEnd(_PositionToken):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Union[str, Set[str]]
    def __init__(self) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Union[str, List[nothing]]]: ...

class LineStart(_PositionToken):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self) -> None: ...
    def parseImpl(self, instring, loc: _T1, doActions = ...) -> Tuple[_T1, List[nothing]]: ...

class Literal(Token):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    firstMatchChar: Any
    ignoreExprs: List[nothing]
    keepTabs: bool
    match: Any
    matchLen: int
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: set
    def __init__(self, matchString) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...

class MatchFirst(ParseExpression):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    exprs: Any
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    name: str
    parseAction: list
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Union[str, Set[str]]
    def __init__(self, exprs, savelist = ...) -> None: ...
    def __ior__(self, other) -> Any: ...
    def __str__(self) -> Any: ...
    def _setResultsName(self, name, listAllMatches = ...) -> Any: ...
    def checkRecursion(self, parseElementList) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Any: ...
    def streamline(self: _TMatchFirst) -> _TMatchFirst: ...

class NoMatch(Token):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> NoReturn: ...

class NotAny(ParseElementEnhance):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: bool
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, expr) -> None: ...
    def __str__(self) -> Any: ...
    def parseImpl(self, instring, loc: _T1, doActions = ...) -> Tuple[_T1, List[nothing]]: ...

class OneOrMore(_MultipleMatch):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    not_ender: None
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Any
    def __str__(self) -> Any: ...

class OnlyOnce:
    __doc__: str
    callable: Any
    called: bool
    def __call__(self, s, l, t) -> Any: ...
    def __init__(self, methodCall) -> None: ...
    def reset(self) -> None: ...

class Optional(ParseElementEnhance):
    _Optional__optionalNotMatched: _NullToken
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    defaultValue: Any
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: bool
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: typing.Optional[str]
    saveAsList: Any
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Any
    def __init__(self, expr, default = ...) -> None: ...
    def __str__(self) -> Any: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...

class Or(ParseExpression):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    exprs: list
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, exprs, savelist = ...) -> None: ...
    def __ixor__(self, other) -> Any: ...
    def __str__(self) -> Any: ...
    def _setResultsName(self, name, listAllMatches = ...) -> Any: ...
    def checkRecursion(self, parseElementList) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Any: ...
    def streamline(self: _TOr) -> _TOr: ...

class ParseBaseException(Exception):
    __doc__: str
    __traceback__: Any
    args: Tuple[Any, Any, Any]
    loc: Any
    msg: Any
    parserElement: Any
    pstr: Any
    def __dir__(self) -> List[str]: ...
    def __getattr__(self, aname) -> Any: ...
    def __init__(self, pstr, loc = ..., msg = ..., elem = ...) -> None: ...
    def __repr__(self) -> Any: ...
    def __str__(self) -> str: ...
    @classmethod
    def _from_exception(cls: Type[_TParseBaseException], pe) -> _TParseBaseException: ...
    def markInputline(self, markerString = ...) -> Any: ...

class ParseElementEnhance(ParserElement):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: Any
    strRepr: typing.Optional[str]
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, expr, savelist = ...) -> None: ...
    def __str__(self) -> Any: ...
    def checkRecursion(self, parseElementList) -> None: ...
    def ignore(self: _TParseElementEnhance, other) -> _TParseElementEnhance: ...
    def leaveWhitespace(self: _TParseElementEnhance) -> _TParseElementEnhance: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Any: ...
    def streamline(self: _TParseElementEnhance) -> _TParseElementEnhance: ...
    def validate(self, validateTrace = ...) -> None: ...

class ParseException(ParseBaseException):
    __doc__: str
    __traceback__: None
    args: Tuple[Any, Any, Any]
    loc: Any
    msg: Any
    parserElement: Any
    pstr: Any
    @staticmethod
    def explain(exc, depth = ...) -> str: ...

class ParseExpression(ParserElement):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    exprs: Any
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: bool
    strRepr: typing.Optional[str]
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, exprs, savelist = ...) -> None: ...
    def __str__(self) -> Any: ...
    def _setResultsName(self, name, listAllMatches = ...) -> Any: ...
    def append(self: _TParseExpression, other) -> _TParseExpression: ...
    def copy(self) -> Any: ...
    def ignore(self: _TParseExpression, other) -> _TParseExpression: ...
    def leaveWhitespace(self: _TParseExpression) -> _TParseExpression: ...
    def streamline(self: _TParseExpression) -> _TParseExpression: ...
    def validate(self, validateTrace = ...) -> None: ...

class ParseFatalException(ParseBaseException):
    __doc__: str
    args: Tuple[Any, Any, Any]
    loc: Any
    msg: Any
    parserElement: Any
    pstr: Any

class ParseResults:
    _ParseResults__accumNames: dict
    _ParseResults__asList: Any
    _ParseResults__doinit: bool
    _ParseResults__modal: Any
    _ParseResults__name: Any
    _ParseResults__parent: typing.Optional[_weakref.ReferenceType[nothing]]
    _ParseResults__tokdict: Any
    _ParseResults__toklist: Any
    __doc__: str
    def _ParseResults__lookup(self, sub) -> None: ...
    def __add__(self, other) -> Any: ...
    def __bool__(self) -> bool: ...
    def __contains__(self, k) -> bool: ...
    def __delitem__(self, i) -> None: ...
    def __dir__(self) -> list: ...
    def __getattr__(self, name) -> Any: ...
    def __getitem__(self, i) -> Any: ...
    def __getnewargs__(self) -> Tuple[Any, Any, Any, Any]: ...
    def __getstate__(self) -> Tuple[Any, Tuple[typing.Dict[nothing, nothing], Any, dict, Any]]: ...
    def __iadd__(self: _TParseResults, other) -> _TParseResults: ...
    def __init__(self, toklist = ..., name = ..., asList = ..., modal = ..., isinstance = ...) -> None: ...
    def __iter__(self) -> Any: ...
    def __len__(self) -> int: ...
    def __new__(cls, toklist: _T0 = ..., name = ..., asList = ..., modal = ...) -> Union[ParseResults, _T0]: ...
    def __nonzero__(self) -> bool: ...
    def __radd__(self, other) -> Any: ...
    def __repr__(self) -> str: ...
    def __reversed__(self) -> Any: ...
    def __setitem__(self, k, v, isinstance = ...) -> None: ...
    def __setstate__(self, state) -> None: ...
    def __str__(self) -> str: ...
    def _asStringList(self, sep = ...) -> list: ...
    def _iteritems(self) -> Any: ...
    def _iterkeys(self) -> Any: ...
    def _itervalues(self) -> Any: ...
    def append(self, item) -> None: ...
    def asDict(self) -> dict: ...
    def asList(self) -> Any: ...
    def asXML(self, doctag = ..., namedItemsOnly = ..., indent = ..., formatted = ...) -> str: ...
    def clear(self) -> None: ...
    def copy(self) -> Any: ...
    def dump(self, indent = ..., full = ..., include_list = ..., _depth = ...) -> str: ...
    def extend(self, itemseq) -> None: ...
    @classmethod
    def from_dict(cls, other, name = ...) -> Any: ...
    def get(self, key, defaultValue = ...) -> Any: ...
    def getName(self) -> Any: ...
    def haskeys(self) -> bool: ...
    def insert(self, index, insStr) -> None: ...
    def items(self) -> list: ...
    def iteritems(self) -> Any: ...
    def iterkeys(self) -> Any: ...
    def itervalues(self) -> Any: ...
    def keys(self) -> list: ...
    def pop(self, *args, **kwargs) -> Any: ...
    def pprint(self, *args, **kwargs) -> None: ...
    def values(self) -> list: ...

class ParseSyntaxException(ParseFatalException):
    __doc__: str
    args: Tuple[Any, Any, Any]
    loc: Any
    msg: Any
    parserElement: Any
    pstr: Any

class ParserElement:
    DEFAULT_WHITE_CHARS: Any
    _FifoCache: type
    _UnboundedCache: type
    __doc__: str
    _literalStringClass: Any
    _packratEnabled: Any
    _parse: Any
    callDuringTry: Any
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[Any, Any, Any]
    errmsg: str
    failAction: Any
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    packrat_cache: Any
    packrat_cache_lock: Any
    packrat_cache_stats: list
    parseAction: list
    re: None
    resultsName: None
    saveAsList: Any
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    verbose_stacktrace: bool
    whiteChars: Any
    def __add__(self, other) -> typing.Optional[Union[And, _PendingSkip]]: ...
    def __and__(self, other) -> typing.Optional[Each]: ...
    def __call__(self, name = ...) -> Any: ...
    def __eq__(self, other) -> Any: ...
    def __getitem__(self, key) -> Any: ...
    def __hash__(self) -> int: ...
    def __init__(self, savelist = ...) -> None: ...
    def __invert__(self) -> NotAny: ...
    def __iter__(self) -> NoReturn: ...
    def __mul__(self, other) -> Any: ...
    def __ne__(self, other) -> bool: ...
    def __or__(self, other) -> typing.Optional[Union[MatchFirst, _PendingSkip]]: ...
    def __radd__(self, other) -> Any: ...
    def __rand__(self, other) -> Any: ...
    def __repr__(self) -> Any: ...
    def __req__(self, other) -> Any: ...
    def __rmul__(self, other) -> Any: ...
    def __rne__(self, other) -> bool: ...
    def __ror__(self, other) -> Any: ...
    def __rsub__(self, other) -> Any: ...
    def __rxor__(self, other) -> Any: ...
    def __str__(self) -> Any: ...
    def __sub__(self, other) -> Any: ...
    def __xor__(self, other) -> typing.Optional[Or]: ...
    def _parseCache(self, instring, loc, doActions = ..., callPreParse = ...) -> Any: ...
    def _parseNoCache(self, instring, loc, doActions = ..., callPreParse = ...) -> Tuple[Any, Any]: ...
    def _setResultsName(self, name, listAllMatches = ...) -> Any: ...
    def _skipIgnorables(self, instring, loc) -> NoReturn: ...
    @classmethod
    def _trim_traceback(cls, tb: _T0) -> _T0: ...
    def addCondition(self: _TParserElement, *fns, **kwargs) -> _TParserElement: ...
    def addParseAction(self: _TParserElement, *fns, **kwargs) -> _TParserElement: ...
    def canParseNext(self, instring, loc) -> bool: ...
    def checkRecursion(self, parseElementList) -> None: ...
    def copy(self: _TParserElement) -> _TParserElement: ...
    @staticmethod
    def enablePackrat(cache_size_limit = ...) -> None: ...
    def ignore(self: _TParserElement, other) -> _TParserElement: ...
    @staticmethod
    def inlineLiteralsUsing(cls) -> None: ...
    def leaveWhitespace(self: _TParserElement) -> _TParserElement: ...
    def matches(self, testString, parseAll = ...) -> bool: ...
    def parseFile(self, file_or_filename, parseAll = ...) -> Any: ...
    def parseImpl(self, instring, loc: _T1, doActions = ...) -> Tuple[_T1, List[nothing]]: ...
    def parseString(self, instring, parseAll = ...) -> Any: ...
    def parseWithTabs(self: _TParserElement) -> _TParserElement: ...
    def postParse(self, instring, loc, tokenlist: _T2) -> _T2: ...
    def preParse(self, instring, loc) -> Any: ...
    @staticmethod
    def resetCache() -> None: ...
    def runTests(self, tests, parseAll = ..., comment = ..., fullDump = ..., printResults = ..., failureTests: _T5 = ..., postParse = ..., file = ...) -> Tuple[Union[bool, _T5], List[Tuple[Any, Any]]]: ...
    def scanString(self, instring, maxMatches = ..., overlap = ...) -> Generator[Tuple[Any, Any, Any], Any, None]: ...
    def searchString(self, instring, maxMatches = ...) -> Any: ...
    def setBreak(self: _TParserElement, breakFlag = ...) -> _TParserElement: ...
    def setDebug(self: _TParserElement, flag = ...) -> _TParserElement: ...
    def setDebugActions(self: _TParserElement, startAction, successAction, exceptionAction) -> _TParserElement: ...
    @staticmethod
    def setDefaultWhitespaceChars(chars) -> None: ...
    def setFailAction(self: _TParserElement, fn) -> _TParserElement: ...
    def setName(self: _TParserElement, name) -> _TParserElement: ...
    def setParseAction(self: _TParserElement, *fns, **kwargs) -> _TParserElement: ...
    def setResultsName(self, name, listAllMatches = ...) -> Any: ...
    def setWhitespaceChars(self: _TParserElement, chars) -> _TParserElement: ...
    def split(self, instring, maxsplit = ..., includeSeparators = ...) -> Generator[Any, Any, None]: ...
    def streamline(self: _TParserElement) -> _TParserElement: ...
    def suppress(self) -> Suppress: ...
    def transformString(self, instring) -> str: ...
    def tryParse(self, instring, loc) -> Any: ...
    def validate(self, validateTrace = ...) -> None: ...

class PrecededBy(ParseElementEnhance):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    exact: bool
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    parseAction: List[Callable[[Any, Any, Any], Any]]
    re: None
    resultsName: None
    retreat: Any
    saveAsList: Any
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, expr, retreat = ...) -> None: ...
    def parseImpl(self, instring, loc: _T1 = ..., doActions = ...) -> Tuple[_T1, Any]: ...

class QuotedString(Token):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    convertWhitespaceEscapes: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    endQuoteChar: Any
    endQuoteCharLen: int
    errmsg: str
    escChar: Any
    escCharReplacePattern: Any
    escQuote: Any
    failAction: None
    firstQuoteChar: Any
    flags: int
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    pattern: str
    quoteChar: Any
    quoteCharLen: int
    re: typing.Optional[Pattern[str]]
    reString: str
    re_match: Callable
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: typing.Optional[str]
    streamlined: bool
    unquoteResults: Any
    whiteChars: Set[str]
    def __init__(self, quoteChar, escChar = ..., escQuote = ..., multiline = ..., unquoteResults = ..., endQuoteChar = ..., convertWhitespaceEscapes = ...) -> None: ...
    def __str__(self) -> Any: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[int, Any]: ...

class RecursiveGrammarException(Exception):
    __doc__: str
    parseElementTrace: Any
    def __init__(self, parseElementList) -> None: ...
    def __str__(self) -> str: ...

class Regex(Token):
    __doc__: str
    asGroupList: Any
    asMatch: Any
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    failAction: None
    flags: Any
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: Any
    parseImpl: Any
    pattern: Any
    re: Any
    reString: Any
    re_match: Any
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: typing.Optional[str]
    streamlined: bool
    whiteChars: Union[str, Set[str]]
    def __init__(self, pattern, flags = ..., asGroupList = ..., asMatch = ...) -> None: ...
    def __str__(self) -> Any: ...
    def parseImplAsGroupList(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...
    def parseImplAsMatch(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...
    def sub(self, repl) -> Any: ...

class SkipTo(ParseElementEnhance):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    failOn: Any
    ignoreExpr: Any
    ignoreExprs: list
    includeMatch: Any
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: set
    def __init__(self, other, include = ..., ignore = ..., failOn = ...) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...

class StringEnd(_PositionToken):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self) -> None: ...
    def parseImpl(self, instring, loc: _T1, doActions = ...) -> Tuple[Any, List[nothing]]: ...

class StringStart(_PositionToken):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self) -> None: ...
    def parseImpl(self, instring, loc: _T1, doActions = ...) -> Tuple[_T1, List[nothing]]: ...

class Suppress(TokenConverter):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Any
    def postParse(self, instring, loc, tokenlist) -> List[nothing]: ...
    def suppress(self: _TSuppress) -> _TSuppress: ...

class Token(ParserElement):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self) -> None: ...

class TokenConverter(ParseElementEnhance):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, expr, savelist = ...) -> None: ...

class White(Token):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    matchWhite: Any
    maxLen: Any
    mayIndexError: bool
    mayReturnEmpty: bool
    minLen: Any
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Union[str, Set[str]]
    whiteStrs: typing.Dict[str, str]
    def __init__(self, ws = ..., min = ..., max = ..., exact = ...) -> None: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...

class Word(Token):
    __doc__: str
    asKeyword: Any
    bodyChars: set
    bodyCharsOrig: Any
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    initChars: set
    initCharsOrig: Any
    keepTabs: bool
    maxLen: Any
    maxSpecified: Any
    mayIndexError: bool
    mayReturnEmpty: bool
    minLen: Any
    modalResults: bool
    name: Any
    parseAction: list
    re: typing.Optional[Pattern[str]]
    reString: str
    re_match: Callable
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: typing.Optional[str]
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, initChars, bodyChars = ..., min = ..., max = ..., exact = ..., asKeyword = ..., excludeChars = ...) -> None: ...
    def __str__(self) -> Any: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...

class WordEnd(_PositionToken):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    wordChars: set
    def __init__(self, wordChars = ...) -> None: ...
    def parseImpl(self, instring, loc: _T1, doActions = ...) -> Tuple[_T1, List[nothing]]: ...

class WordStart(_PositionToken):
    __doc__: str
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    wordChars: set
    def __init__(self, wordChars = ...) -> None: ...
    def parseImpl(self, instring, loc: _T1, doActions = ...) -> Tuple[_T1, List[nothing]]: ...

class ZeroOrMore(_MultipleMatch):
    __doc__: str
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: bool
    modalResults: bool
    not_ender: None
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, expr, stopOn = ...) -> None: ...
    def __str__(self) -> Any: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Any: ...

class _MultipleMatch(ParseElementEnhance):
    callDuringTry: bool
    callPreparse: Any
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    expr: Any
    failAction: None
    ignoreExprs: list
    keepTabs: bool
    mayIndexError: Any
    mayReturnEmpty: Any
    modalResults: bool
    not_ender: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: Any
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self, expr, stopOn = ...) -> None: ...
    def _setResultsName(self, name, listAllMatches = ...) -> Any: ...
    def parseImpl(self, instring, loc, doActions = ...) -> Any: ...
    def stopOn(self: _T_MultipleMatch, ender) -> _T_MultipleMatch: ...

class _NullToken:
    def __bool__(self) -> bool: ...
    def __nonzero__(self) -> bool: ...
    def __str__(self) -> str: ...

class _ParseResultsWithOffset:
    tup: Tuple[Any, Any]
    def __getitem__(self, i) -> Any: ...
    def __init__(self, p1, p2) -> None: ...
    def __repr__(self) -> str: ...
    def setOffset(self, i) -> None: ...

class _PendingSkip(ParserElement):
    anchor: Any
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[typing.Optional[Callable[[Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any, Any], Any]], typing.Optional[Callable[[Any, Any, Any, Any], Any]]]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    must_skip: Any
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: str
    streamlined: bool
    whiteChars: Set[str]
    def __add__(self, other) -> Any: ...
    def __init__(self, expr, must_skip = ...) -> None: ...
    def __repr__(self) -> str: ...
    def parseImpl(self, *args) -> NoReturn: ...

class _PositionToken(Token):
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    keepTabs: bool
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def __init__(self) -> None: ...

class _SingleCharLiteral(Literal):
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    firstMatchChar: Any
    ignoreExprs: List[nothing]
    keepTabs: bool
    match: Any
    matchLen: int
    mayIndexError: bool
    mayReturnEmpty: bool
    modalResults: bool
    name: str
    parseAction: List[nothing]
    re: None
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[Any, Any]: ...

class _WordRegex(Word):
    asKeyword: Any
    bodyChars: set
    bodyCharsOrig: Any
    callDuringTry: bool
    callPreparse: bool
    copyDefaultWhiteChars: bool
    debug: bool
    debugActions: Tuple[None, None, None]
    errmsg: str
    failAction: None
    ignoreExprs: List[nothing]
    initChars: set
    initCharsOrig: Any
    keepTabs: bool
    maxLen: Any
    maxSpecified: Any
    mayIndexError: bool
    mayReturnEmpty: bool
    minLen: Any
    modalResults: bool
    name: Any
    parseAction: List[nothing]
    re: typing.Optional[Pattern[str]]
    reString: str
    re_match: Callable
    resultsName: None
    saveAsList: bool
    skipWhitespace: bool
    strRepr: None
    streamlined: bool
    whiteChars: Set[str]
    def parseImpl(self, instring, loc, doActions = ...) -> Tuple[int, str]: ...

class _lazyclassproperty:
    __doc__: Any
    fn: Any
    def __get__(self, obj, cls) -> Any: ...
    def __init__(self, fn) -> None: ...

class pyparsing_common:
    __doc__: str
    _commasepitem: Combine
    _full_ipv6_address: Union[And, _PendingSkip]
    _html_stripper: Any
    _ipv6_part: Regex
    _mixed_ipv6_address: Any
    _short_ipv6_address: And
    comma_separated_list: And
    fnumber: Regex
    fraction: And
    hex_integer: Any
    identifier: Any
    integer: Any
    ipv4_address: Regex
    ipv6_address: Combine
    iso8601_date: Regex
    iso8601_datetime: Regex
    mac_address: Regex
    mixed_integer: MatchFirst
    number: MatchFirst
    real: Regex
    sci_real: Regex
    signed_integer: Regex
    uuid: Regex
    @staticmethod
    def convertToDate(fmt = ...) -> Callable[[Any, Any, Any], Any]: ...
    @staticmethod
    def convertToDatetime(fmt = ...) -> Callable[[Any, Any, Any], Any]: ...
    def convertToFloat(s: pyparsing_common, l, t) -> Any: ...
    def convertToInteger(s: pyparsing_common, l, t) -> Any: ...
    @staticmethod
    def downcaseTokens(s, l, t) -> Any: ...
    @staticmethod
    def stripHTMLTags(s, l, tokens) -> Any: ...
    @staticmethod
    def upcaseTokens(s, l, t) -> Any: ...

class pyparsing_test:
    TestParseResultsAsserts: type
    __doc__: str
    reset_pyparsing_context: type

class pyparsing_unicode(unicode_set):
    Arabic: type
    CJK: type
    Chinese: type
    Cyrillic: type
    Devanagari: type
    Greek: type
    Hebrew: type
    Japanese: type
    Korean: type
    Latin1: type
    LatinA: type
    LatinB: type
    Thai: type
    __doc__: str
    _ranges: List[Tuple[int, int]]

class unicode_set:
    __doc__: str
    _ranges: List[nothing]
    alphanums: Any
    alphas: Any
    nums: Any
    printables: Any
    @classmethod
    def _get_chars_for_ranges(cls) -> Any: ...

def _defaultExceptionDebugAction(instring, loc, expr, exc) -> None: ...
def _defaultStartDebugAction(instring, loc, expr) -> None: ...
def _defaultSuccessDebugAction(instring, startloc, endloc, expr, toks) -> None: ...
def _enable_all_warnings() -> None: ...
def _escapeRegexRangeChars(s) -> Any: ...
def _flatten(L) -> list: ...
def _makeTags(tagStr, xml, suppress_LT = ..., suppress_GT = ...) -> Tuple[Any, Any]: ...
def _trim_arity(func, maxargs = ...) -> Callable: ...
def _xml_escape(data) -> Any: ...
def col(loc, strg) -> Any: ...
def conditionAsParseAction(fn, message = ..., fatal = ...) -> Callable: ...
def contextmanager(func: Callable[..., Iterator[_T]]) -> Callable[..., contextlib._GeneratorContextManager[_T]]: ...
def countedArray(expr, intExpr = ...) -> Any: ...
def delimitedList(expr, delim = ..., combine = ...) -> Any: ...
def dictOf(key, value) -> Dict: ...
def downcaseTokens(s, l, t) -> Any: ...
def indentedBlock(blockStatementExpr, indentStack, indent = ...) -> Any: ...
def infixNotation(baseExpr, opList, lpar = ..., rpar = ...) -> Any: ...
def itemgetter(*items) -> Callable[[Any], tuple]: ...
def line(loc, strg) -> Any: ...
def lineno(loc, strg) -> Any: ...
def locatedExpr(expr) -> Group: ...
def makeHTMLTags(tagStr) -> Any: ...
def makeXMLTags(tagStr) -> Any: ...
def matchOnlyAtCol(n) -> Callable[[Any, Any, Any], Any]: ...
def matchPreviousExpr(expr) -> Any: ...
def matchPreviousLiteral(expr) -> Forward: ...
def nestedExpr(opener = ..., closer = ..., content = ..., ignoreExpr = ...) -> Any: ...
def nullDebugAction(*args) -> None: ...
def oneOf(strs, caseless = ..., useRegex = ..., asKeyword = ...) -> Any: ...
def operatorPrecedence(baseExpr, opList, lpar = ..., rpar = ...) -> Any: ...
def originalTextFor(expr, asString = ...) -> Any: ...
def removeQuotes(s, l, t) -> Any: ...
def replaceHTMLEntity(t) -> typing.Optional[str]: ...
def replaceWith(replStr) -> Callable[[Any, Any, Any], Any]: ...
def srange(s) -> str: ...
def tokenMap(func, *args) -> Callable[[Any, Any, Any], Any]: ...
def traceParseAction(f) -> Callable: ...
def ungroup(expr) -> Any: ...
def unichr(i: int) -> str: ...
def upcaseTokens(s, l, t) -> Any: ...
def withAttribute(*args, **attrDict) -> Callable[[Any, Any, Any], Any]: ...
def withClass(classname, namespace = ...) -> Any: ...
def wraps(wrapped: Callable, assigned: Sequence[str] = ..., updated: Sequence[str] = ...) -> Callable[[Callable], Callable]: ...
