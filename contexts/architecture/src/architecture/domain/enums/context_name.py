from enum import StrEnum, auto


class ContextName(StrEnum):
    ARCHITECTURE = auto()
    CODEGEN = auto()
    PANGU_CLI = auto()
    FOUNDATION = auto()