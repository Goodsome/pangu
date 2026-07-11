from __future__ import annotations
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Literal
from typing import Optional
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstRaise(AstStmtBase):
    kind: Literal[AstStmtKind.RAISE] = AstStmtKind.RAISE
    exc: Optional[AstExprBase] = None
    cause: Optional[AstExprBase] = None
