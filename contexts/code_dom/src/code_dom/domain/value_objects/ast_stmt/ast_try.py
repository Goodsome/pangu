from __future__ import annotations
from typing import Literal
from pydantic import Field
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.value_objects.ast_stmt.ast_except_handler import (
    AstExceptHandler,
)
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstTry(AstStmtBase):
    kind: Literal[AstStmtKind.TRY] = AstStmtKind.TRY
    body: list[AstStmtBase] = Field(default_factory=list)
    handlers: list[AstExceptHandler] = Field(default_factory=list)
    orelse: list[AstStmtBase] = Field(default_factory=list)
    finalbody: list[AstStmtBase] = Field(default_factory=list)
    is_star: bool = False
