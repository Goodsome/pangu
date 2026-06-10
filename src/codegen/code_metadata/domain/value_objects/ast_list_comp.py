from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.value_objects.ast_comprehension import (
    AstComprehension,
)
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstListComp(ValueObject):
    kind: Literal[AstExprKind.LIST_COMP] = AstExprKind.LIST_COMP
    elt: AstExpr
    generators: list[AstComprehension] = Field(default_factory=list)
