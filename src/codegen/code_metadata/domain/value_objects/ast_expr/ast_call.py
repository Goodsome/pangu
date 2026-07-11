from __future__ import annotations
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.ast_keyword import AstKeyword
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstCall(AstExprBase):
    kind: Literal[AstExprKind.CALL] = AstExprKind.CALL
    func: AstExprBase
    args: list[AstExprBase] = Field(default_factory=list)
    kwargs: list[AstKeyword] = Field(default_factory=list)
