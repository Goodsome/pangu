from __future__ import annotations
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Literal
from pydantic import Field
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.value_objects.ast_stmt.ast_match_case import AstMatchCase
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstMatch(AstStmtBase):
    kind: Literal[AstStmtKind.MATCH] = AstStmtKind.MATCH
    subject: AstExprBase
    cases: list[AstMatchCase] = Field(default_factory=list)
