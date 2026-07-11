from __future__ import annotations
from typing import Literal
from pydantic import Field
from code_dom.domain.enums.ast_stmt_kind import AstStmtKind
from code_dom.domain.value_objects.ast_stmt.ast_with_item import AstWithItem
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase



class AstWith(AstStmtBase):
    kind: Literal[AstStmtKind.WITH] = AstStmtKind.WITH
    items: list[AstWithItem] = Field(default_factory=list)
    body: list[AstStmtBase] = Field(default_factory=list)
    is_async: bool = False
