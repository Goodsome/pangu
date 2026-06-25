from enum import StrEnum, auto


class ArchitectureLayer(StrEnum):
    DOMAIN = auto()
    APPLICATION = auto()
    INFRASTRUCTURE = auto()
    INTERFACES = auto()
    