from enum import StrEnum, auto


class ScaffoldType(StrEnum):
    COMMAND = auto()
    METHOD = auto()
    DOMAIN_SERVICE = auto()
