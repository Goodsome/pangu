from __future__ import annotations
from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.enums.unary_op import UnaryOp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstUnaryOp(AstExprBase):
    kind: Literal[AstExprKind.UNARY_OP] = AstExprKind.UNARY_OP
    op: UnaryOp
    operand: AstExprBase
