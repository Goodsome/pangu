from __future__ import annotations
from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstAttribute(AstExprBase):
    kind: Literal[AstExprKind.ATTRIBUTE] = AstExprKind.ATTRIBUTE
    value: AstExprBase
    attr: str
