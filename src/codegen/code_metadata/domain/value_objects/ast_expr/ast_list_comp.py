from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.ast_comprehension import (
    AstComprehension,
)
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstListComp(AstExprBase):
    kind: Literal[AstExprKind.LIST_COMP] = AstExprKind.LIST_COMP
    elt: AstExprBase
    generators: list[AstComprehension] = Field(default_factory=list)
