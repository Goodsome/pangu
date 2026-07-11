from __future__ import annotations
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from foundation.building_blocks.value_object import ValueObject

class Arg(ValueObject):
    """Represents a single function/lambda parameter."""

    arg: str
    annotation: AstExprBase | None = None
