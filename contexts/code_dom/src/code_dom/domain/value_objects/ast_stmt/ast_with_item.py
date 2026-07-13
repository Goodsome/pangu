from __future__ import annotations

from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from foundation.building_blocks.value_object import ValueObject


class AstWithItem(ValueObject):
    context_expr: AstExprBase
    optional_vars: AstExprBase | None = None
