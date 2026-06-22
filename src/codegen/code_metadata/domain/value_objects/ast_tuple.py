from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from foundation.building_blocks.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstTuple(ValueObject):
    kind: Literal[AstExprKind.TUPLE] = AstExprKind.TUPLE
    elts: list[AstExpr] = Field(default_factory=list)
