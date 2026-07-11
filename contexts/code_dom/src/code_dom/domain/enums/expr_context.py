from enum import StrEnum
from enum import auto


class ExprContext(StrEnum):
    LOAD = auto()
    STORE = auto()
    DEL = auto()
