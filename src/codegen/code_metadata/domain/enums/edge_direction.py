from enum import StrEnum
from enum import auto


class EdgeDirection(StrEnum):
    """追踪方向：上游（依赖者）或下游（被依赖者）。"""

    OUT = auto()
    IN = auto()
