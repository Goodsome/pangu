from enum import StrEnum
from enum import auto


class BinOp(StrEnum):
    ADD = auto()
    SUB = auto()
    MULT = auto()
    DIV = auto()
    FLOOR_DIV = auto()
    MOD = auto()
    POW = auto()
    LSHIFT = auto()
    RSHIFT = auto()
    BIT_OR = auto()
    BIT_XOR = auto()
    BIT_AND = auto()
    MAT_MULT = auto()
