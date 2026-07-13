from __future__ import annotations
from typing import Literal
from pydantic import Field
from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.value_objects.ast_expr.ast_comprehension import (
    AstComprehension,
)
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase


class AstSetComp(AstExprBase):
    kind: Literal[AstExprKind.SET_COMP] = AstExprKind.SET_COMP
    elt: AstExprBase
    generators: list[AstComprehension] = Field(default_factory=list)
