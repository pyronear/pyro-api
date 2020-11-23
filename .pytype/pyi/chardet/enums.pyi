# (generated with --quick)

class CharacterCategory:
    CONTROL: int
    DIGIT: int
    LINE_BREAK: int
    SYMBOL: int
    UNDEFINED: int
    __doc__: str

class InputState:
    ESC_ASCII: int
    HIGH_BYTE: int
    PURE_ASCII: int
    __doc__: str

class LanguageFilter:
    ALL: int
    CHINESE: int
    CHINESE_SIMPLIFIED: int
    CHINESE_TRADITIONAL: int
    CJK: int
    JAPANESE: int
    KOREAN: int
    NON_CJK: int
    __doc__: str

class MachineState:
    ERROR: int
    ITS_ME: int
    START: int
    __doc__: str

class ProbingState:
    DETECTING: int
    FOUND_IT: int
    NOT_ME: int
    __doc__: str

class SequenceLikelihood:
    LIKELY: int
    NEGATIVE: int
    POSITIVE: int
    UNLIKELY: int
    __doc__: str
    @classmethod
    def get_num_categories(cls) -> int: ...
