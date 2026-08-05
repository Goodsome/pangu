from typing import Literal
from pydantic import Field
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase


class AstGlobal(AstStmtBase):
    kind: Literal[AstStmtKind.GLOBAL] = AstStmtKind.GLOBAL
    names: list[str] = Field(default_factory=list)


class AstNonlocal(AstStmtBase):
    kind: Literal[AstStmtKind.NONLOCAL] = AstStmtKind.NONLOCAL
    names: list[str] = Field(default_factory=list)
