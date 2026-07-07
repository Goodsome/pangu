from enum import auto, StrEnum

class MethodType(StrEnum):
    INSTANCE = auto()
    STATIC = auto()
    CLASS = auto()