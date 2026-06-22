from __future__ import annotations
from typing import Optional
from foundation.building_blocks.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstWithItem(ValueObject):
    context_expr: AstExpr
    optional_vars: Optional[AstExpr] = None
