from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_stmt_kind import AstStmtKind
from codegen.code_metadata.domain.value_objects.ast_with_item import AstWithItem
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_stmt_old import AstStmt


class AstWith(ValueObject):
    kind: Literal[AstStmtKind.WITH] = AstStmtKind.WITH
    items: list[AstWithItem] = Field(default_factory=list)
    body: list[AstStmt] = Field(default_factory=list)
    is_async: bool = False
