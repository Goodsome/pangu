from __future__ import annotations
from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.enums.bin_op import BinOp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstBinOp(AstExprBase):
    kind: Literal[AstExprKind.BIN_OP] = AstExprKind.BIN_OP
    left: AstExprBase
    op: BinOp
    right: AstExprBase
