from __future__ import annotations
from typing import Literal
from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.enums.bin_op import BinOp
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstBinOp(AstExprBase):
    kind: Literal[AstExprKind.BIN_OP] = AstExprKind.BIN_OP
    left: AstExprBase
    op: BinOp
    right: AstExprBase
