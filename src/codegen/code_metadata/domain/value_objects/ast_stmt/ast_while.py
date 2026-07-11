from __future__ import annotations
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase



class AstWhile(AstStmtBase):
    kind: Literal[AstStmtKind.WHILE] = AstStmtKind.WHILE
    test: AstExprBase
    body: list[AstStmtBase] = Field(default_factory=list)
    orelse: list[AstStmtBase] = Field(default_factory=list)
