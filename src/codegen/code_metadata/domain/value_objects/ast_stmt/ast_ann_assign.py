from __future__ import annotations
from typing import Literal
from typing import Optional
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstAnnAssign(AstStmtBase):
    kind: Literal[AstStmtKind.ANN_ASSIGN] = AstStmtKind.ANN_ASSIGN
    target: AstExpr
    annotation: AstExpr
    value: Optional[AstExpr] = None
    simple: int = 1
