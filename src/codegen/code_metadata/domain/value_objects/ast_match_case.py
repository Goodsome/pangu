from __future__ import annotations
from typing import Optional
from pydantic import Field
from codegen.code_metadata.domain.value_objects.match_pattern import MatchPattern
from foundation.building_blocks.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr



class AstMatchCase(ValueObject):
    pattern: MatchPattern
    guard: Optional[AstExpr] = None
    body: list[AstStmtBase] = Field(default_factory=list)
