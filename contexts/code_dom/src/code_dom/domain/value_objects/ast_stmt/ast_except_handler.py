from __future__ import annotations

from pydantic import Field

from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from foundation.building_blocks.value_object import ValueObject


class AstExceptHandler(ValueObject):
    type: AstExprBase | None = None
    name: str | None = None
    body: list[AstStmtBase] = Field(default_factory=list)
