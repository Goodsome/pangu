from __future__ import annotations
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr



class AstIf(AstStmtBase):
    kind: Literal[AstStmtKind.IF] = AstStmtKind.IF
    test: AstExpr
    body: list[AstStmtBase] = Field(default_factory=list)
    orelse: list[AstStmtBase] = Field(default_factory=list)
