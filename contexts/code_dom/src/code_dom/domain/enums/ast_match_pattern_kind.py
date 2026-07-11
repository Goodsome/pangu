from enum import StrEnum
from enum import auto


class AstMatchPatternKind(StrEnum):
    MATCH_VALUE = auto()
    MATCH_SINGLETON = auto()
    MATCH_SEQUENCE = auto()
    MATCH_MAPPING = auto()
    MATCH_CLASS = auto()
    MATCH_STAR = auto()
    MATCH_AS = auto()
    MATCH_OR = auto()
