from __future__ import annotations
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase

class AstFor(AstStmtBase):
    kind: Literal[AstStmtKind.FOR] = AstStmtKind.FOR
    target: AstExpr
    iter: AstExpr
    body: list[AstStmtBase] = Field(default_factory=list)
    orelse: list[AstStmtBase] = Field(default_factory=list)
