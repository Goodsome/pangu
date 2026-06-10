from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.enums.bin_op import BinOp
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstBinOp(ValueObject):
    kind: Literal[AstExprKind.BIN_OP] = AstExprKind.BIN_OP
    left: AstExpr
    op: BinOp
    right: AstExpr
