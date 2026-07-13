from __future__ import annotations
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Optional
from pydantic import Field
from foundation.building_blocks.value_object import ValueObject


class AstExceptHandler(ValueObject):
    type: Optional[AstExprBase] = None
    name: Optional[str] = None
    body: list[AstStmtBase] = Field(default_factory=list)
