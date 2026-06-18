from enum import StrEnum
from enum import auto


class CodeNodeKind(StrEnum):
    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()
    METHOD = auto()
    VARIABLE = auto()
    PARAMETER = auto()
    EXTERNAL = auto()
    CLASS_TYPE = auto()
    UNION_TYPE = auto()
    GENERIC_TYPE = auto()
    TYPE_VAR = auto()