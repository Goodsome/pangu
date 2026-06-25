from enum import StrEnum, auto


class ContextName(StrEnum):
    ARCHITECTURE = auto()
    CODE_DOM = auto()
    CODE_STRUCTURE = auto()
    CODEGEN = auto()
    PANGU_CLI = auto()
    FOUNDATION = auto()