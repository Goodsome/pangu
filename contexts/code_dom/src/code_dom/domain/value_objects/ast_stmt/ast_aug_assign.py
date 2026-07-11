from __future__ import annotations
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Literal
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.enums.bin_op import BinOp
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstAugAssign(AstStmtBase):
    kind: Literal[AstStmtKind.AUG_ASSIGN] = AstStmtKind.AUG_ASSIGN
    target: AstExprBase
    op: BinOp
    value: AstExprBase
