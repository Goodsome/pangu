from __future__ import annotations
from enum import StrEnum
from enum import auto


class PrimitiveType(StrEnum):
    """通用原语类型，不依赖具体语言。"""

    STRING = auto()
    INTEGER = auto()
    FLOAT = auto()
    BOOLEAN = auto()
    DATETIME = auto()
    UUID = auto()
    ANY = auto()
    NULL = auto()

    def to_python_builtin(self) -> PythonBuiltinType | None:
        match self:
            case PrimitiveType.STRING:
                return PythonBuiltinType.STR
            case PrimitiveType.NULL:
                return PythonBuiltinType.NONE
            case _:
                return None


class PythonBuiltinType(StrEnum):
    EXCEPTION = "Exception"
    ELLIPSIS = "Ellipsis"
    NONE = "None"
    TUPLE = "tuple"
    STR = "str"
    LIST = "list"
    SET = "set"
    DICT = "dict"
    UNION = "Union"
    INT = "int"
    BOOL = "bool"
    FLOAT = "float"
    T_ID = "T_ID"

    def to_primitive_type(self) -> PrimitiveType | None:
        match self:
            case PythonBuiltinType.STR:
                return PrimitiveType.STRING
            case PythonBuiltinType.NONE:
                return PrimitiveType.NULL
            case _:
                return None
