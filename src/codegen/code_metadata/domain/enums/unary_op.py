from enum import StrEnum
from enum import auto


class UnaryOp(StrEnum):
    NOT = auto()
    INVERT = auto()
    UADD = auto()
    USUB = auto()
