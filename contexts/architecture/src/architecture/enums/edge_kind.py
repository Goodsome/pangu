from enum import StrEnum


class EdgeKind(StrEnum):
    DEPENDS_ON = "DEPENDS_ON"
    CONTAINS = "CONTAINS"