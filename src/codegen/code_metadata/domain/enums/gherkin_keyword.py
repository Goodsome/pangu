from enum import StrEnum
from enum import auto


class GherkinKeyword(StrEnum):
    """Gherkin 语法关键字，用于 BDD 场景步骤的语义标注。"""

    GIVEN = auto()
    WHEN = auto()
    THEN = auto()
    AND = auto()
    BUT = auto()
