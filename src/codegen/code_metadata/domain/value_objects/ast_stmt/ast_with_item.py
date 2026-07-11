from __future__ import annotations
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Optional
from foundation.building_blocks.value_object import ValueObject


class AstWithItem(ValueObject):
    context_expr: AstExprBase
    optional_vars: Optional[AstExprBase] = None
