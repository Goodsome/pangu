from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_except_handler import (
    AstExceptHandler,
)
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstStmt


class AstTry(ValueObject):
    kind: Literal[AstStmtKind.TRY] = AstStmtKind.TRY
    body: list[AstStmt] = Field(default_factory=list)
    handlers: list[AstExceptHandler] = Field(default_factory=list)
    orelse: list[AstStmt] = Field(default_factory=list)
    finalbody: list[AstStmt] = Field(default_factory=list)
