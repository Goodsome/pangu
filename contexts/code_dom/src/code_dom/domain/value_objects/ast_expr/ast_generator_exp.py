from __future__ import annotations
from typing import Literal
from pydantic import Field
from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.value_objects.ast_expr.ast_comprehension import (
    AstComprehension,
)
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstGeneratorExp(AstExprBase):
    kind: Literal[AstExprKind.GENERATOR_EXP] = AstExprKind.GENERATOR_EXP
    elt: AstExprBase
    generators: list[AstComprehension] = Field(default_factory=list)
