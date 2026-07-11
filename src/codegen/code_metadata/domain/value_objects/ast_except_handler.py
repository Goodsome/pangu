from __future__ import annotations
from typing import Optional
from pydantic import Field
from foundation.building_blocks.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_stmt.ast_stmt_base import AstStmtBase
from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr



class AstExceptHandler(ValueObject):
    type: Optional[AstExpr] = None
    name: Optional[str] = None
    body: list[AstStmtBase] = Field(default_factory=list)
