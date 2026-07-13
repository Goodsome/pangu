from __future__ import annotations
from typing import Literal
from pydantic import Field
from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase


class AstTuple(AstExprBase):
    kind: Literal[AstExprKind.TUPLE] = AstExprKind.TUPLE
    elts: list[AstExprBase] = Field(default_factory=list)
