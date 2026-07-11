from __future__ import annotations
from typing import Literal
from typing import Optional
from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstSlice(AstExprBase):
    kind: Literal[AstExprKind.SLICE] = AstExprKind.SLICE
    lower: Optional[AstExprBase] = None
    upper: Optional[AstExprBase] = None
    step: Optional[AstExprBase] = None
