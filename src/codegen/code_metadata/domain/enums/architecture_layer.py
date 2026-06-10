from enum import StrEnum
from enum import auto


class ArchitectureLayer(StrEnum):
    DOMAIN = auto()
    APPLICATION = auto()
    INFRASTRUCTURE = auto()
    INTERFACES = auto()
    UNKNOWN = auto()
