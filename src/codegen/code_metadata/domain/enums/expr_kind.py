from enum import StrEnum
from enum import auto


class ExprKind(StrEnum):
    CALL = auto()
    DICT = auto()
    CONSTANT = auto()
    REFERENCE = auto()
    SEQUENCE = auto()
    LAMBDA = auto()
