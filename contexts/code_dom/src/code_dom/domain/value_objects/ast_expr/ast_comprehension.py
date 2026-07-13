from __future__ import annotations
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from pydantic import Field
from foundation.building_blocks.value_object import ValueObject


class AstComprehension(ValueObject):
    target: AstExprBase
    iter: AstExprBase
    ifs: list[AstExprBase] = Field(default_factory=list)
    is_async: int = 0
