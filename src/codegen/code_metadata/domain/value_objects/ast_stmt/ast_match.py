from __future__ import annotations
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_match_case import AstMatchCase
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstMatch(AstStmtBase):
    kind: Literal[AstStmtKind.MATCH] = AstStmtKind.MATCH
    subject: AstExpr
    cases: list[AstMatchCase] = Field(default_factory=list)
