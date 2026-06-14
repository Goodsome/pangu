from enum import StrEnum
from enum import auto


class CodeNodeKind(StrEnum):
    DIRECTORY = auto()
    FILE = auto()
    MODULE = auto()
    CLASS = auto()
    FUNCTION = auto()
    METHOD = auto()
    VARIABLE = auto()
    PARAMETER = auto()
    EXTERNAL = auto()
