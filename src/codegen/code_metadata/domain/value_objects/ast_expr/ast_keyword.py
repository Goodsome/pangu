from __future__ import annotations
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from foundation.building_blocks.value_object import ValueObject

class AstKeyword(ValueObject):
    arg: str | None
    value: AstExprBase
