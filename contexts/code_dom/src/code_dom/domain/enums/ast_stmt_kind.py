from enum import StrEnum
from enum import auto


class AstStmtKind(StrEnum):
    RETURN = auto()
    RAISE = auto()
    PASS = auto()
    BREAK = auto()
    CONTINUE = auto()
    ASSIGN = auto()
    ANN_ASSIGN = auto()
    AUG_ASSIGN = auto()
    EXPR_STMT = auto()
    FOR = auto()
    WHILE = auto()
    IF = auto()
    WITH = auto()
    MATCH = auto()
    ASSERT = auto()
    TRY = auto()
    FUNCTION_DEF = auto()
    IMPORT = auto()
    IMPORT_FROM = auto()
    CLASS_DEF = auto()
    DELETE = auto()
    GLOBAL = auto()
    NONLOCAL = auto()

