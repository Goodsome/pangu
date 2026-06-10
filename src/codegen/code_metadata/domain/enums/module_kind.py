from enum import StrEnum
from enum import auto


class ModuleKind(StrEnum):
    FILE = auto()
    DIRECTORY = auto()
    EXTERNAL = auto()
