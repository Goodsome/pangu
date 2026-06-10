from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.enums.cmp_op import CmpOp
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstCompare(ValueObject):
    kind: Literal[AstExprKind.COMPARE] = AstExprKind.COMPARE
    left: AstExpr
    ops: list[CmpOp] = Field(default_factory=list)
    comparators: list[AstExpr] = Field(default_factory=list)
