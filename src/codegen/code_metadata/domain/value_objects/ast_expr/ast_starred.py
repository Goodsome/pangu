from __future__ import annotations
from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.enums.expr_context import ExprContext
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstStarred(AstExprBase):
    kind: Literal[AstExprKind.STARRED] = AstExprKind.STARRED
    value: AstExprBase
    ctx: ExprContext | None = None
