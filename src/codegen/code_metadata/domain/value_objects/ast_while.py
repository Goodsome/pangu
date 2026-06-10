from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr
    from codegen.code_metadata.domain.value_objects.ast_stmt import AstStmt


class AstWhile(ValueObject):
    kind: Literal[AstStmtKind.WHILE] = AstStmtKind.WHILE
    test: AstExpr
    body: list[AstStmt] = Field(default_factory=list)
    orelse: list[AstStmt] = Field(default_factory=list)
