from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from foundation.building_blocks.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstStmt


class AstIf(ValueObject):
    kind: Literal[AstStmtKind.IF] = AstStmtKind.IF
    test: AstExpr
    body: list[AstStmt] = Field(default_factory=list)
    orelse: list[AstStmt] = Field(default_factory=list)
