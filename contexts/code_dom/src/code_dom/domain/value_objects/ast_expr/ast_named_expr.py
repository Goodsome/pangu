from __future__ import annotations
from typing import Literal
from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from code_dom.domain.value_objects.ast_expr.ast_name import AstName


class AstNamedExpr(AstExprBase):
    kind: Literal[AstExprKind.NAMED_EXPR] = AstExprKind.NAMED_EXPR
    target: AstName
    value: AstExprBase
