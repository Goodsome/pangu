from __future__ import annotations
from typing import Literal
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstExprStmt(AstStmtBase):
    kind: Literal[AstStmtKind.EXPR_STMT] = AstStmtKind.EXPR_STMT
    value: AstExpr
