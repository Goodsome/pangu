from __future__ import annotations
from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from codegen.code_metadata.domain.value_objects.ast_expr.ast_name import AstName

class AstNamedExpr(AstExprBase):
    kind: Literal[AstExprKind.NAMED_EXPR] = AstExprKind.NAMED_EXPR
    target: AstName
    value: AstExprBase
