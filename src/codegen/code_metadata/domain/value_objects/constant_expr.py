from typing import Literal
from typing import Any
from pydantic import field_serializer
from pydantic import field_validator
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.value_object import ValueObject

_ELLIPSIS_MARKER = "__ellipsis__"


class ConstantExpr(ValueObject):
    """描述字面量，例如: 42, "hello", True"""

    kind: Literal[ExprKind.CONSTANT] = ExprKind.CONSTANT
    value: Any

    @field_serializer("value")
    @classmethod
    def _serialize_value(cls, v: Any) -> Any:
        if v is ...:
            return _ELLIPSIS_MARKER
        return v

    @field_validator("value", mode="before")
    @classmethod
    def _validate_value(cls, v: Any) -> Any:
        if v == _ELLIPSIS_MARKER:
            return ...
        return v

    def get_component_ids(self) -> set[ComponentId]:
        return set()
