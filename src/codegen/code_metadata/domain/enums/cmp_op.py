from enum import StrEnum
from enum import auto


class CmpOp(StrEnum):
    EQ = auto()
    NOT_EQ = auto()
    LT = auto()
    LT_E = auto()
    GT = auto()
    GT_E = auto()
    IS = auto()
    IS_NOT = auto()
    IN = auto()
    NOT_IN = auto()
