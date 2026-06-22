from typing import Any
from typing import Literal
from pydantic import field_serializer
from pydantic import field_validator
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from foundation.building_blocks.value_object import ValueObject

_ELLIPSIS_REPRESENTATION = {"__type__": "builtin_singleton", "name": "Ellipsis"}


class AstConstant(ValueObject):
    kind: Literal[AstExprKind.CONSTANT] = AstExprKind.CONSTANT
    value: Any

    @field_serializer("value")
    @classmethod
    def _serialize_value(cls, v: Any) -> Any:
        if v is ...:
            return _ELLIPSIS_REPRESENTATION
        return v

    @field_validator("value", mode="before")
    @classmethod
    def _validate_value(cls, v: Any) -> Any:
        if isinstance(v, dict) and v == _ELLIPSIS_REPRESENTATION:
            return ...
        return v
