from __future__ import annotations
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Literal
from typing import Optional
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstReturn(AstStmtBase):
    kind: Literal[AstStmtKind.RETURN] = AstStmtKind.RETURN
    value: Optional[AstExprBase] = None
