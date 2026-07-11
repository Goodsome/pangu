from __future__ import annotations
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Literal
from typing import Optional
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstAnnAssign(AstStmtBase):
    kind: Literal[AstStmtKind.ANN_ASSIGN] = AstStmtKind.ANN_ASSIGN
    target: AstExprBase
    annotation: AstExprBase
    value: Optional[AstExprBase] = None
    simple: int = 1
