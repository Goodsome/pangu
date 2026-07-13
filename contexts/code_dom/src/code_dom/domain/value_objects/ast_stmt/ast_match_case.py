from __future__ import annotations
from code_dom.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Optional
from pydantic import Field
from code_dom.domain.value_objects.match_pattern import MatchPattern
from foundation.building_blocks.value_object import ValueObject


class AstMatchCase(ValueObject):
    pattern: MatchPattern
    guard: Optional[AstExprBase] = None
    body: list[AstStmtBase] = Field(default_factory=list)
