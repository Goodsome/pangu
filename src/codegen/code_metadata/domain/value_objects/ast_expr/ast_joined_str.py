from __future__ import annotations
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstJoinedStr(AstExprBase):
    kind: Literal[AstExprKind.JOINED_STR] = AstExprKind.JOINED_STR
    values: list[AstExprBase] = Field(default_factory=list)
