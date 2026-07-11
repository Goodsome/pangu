from __future__ import annotations
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.code_metadata.domain.enums.cmp_op import CmpOp
from codegen.code_metadata.domain.value_objects.ast_expr.ast_expr_base import AstExprBase

class AstCompare(AstExprBase):
    kind: Literal[AstExprKind.COMPARE] = AstExprKind.COMPARE
    left: AstExprBase
    ops: list[CmpOp] = Field(default_factory=list)
    comparators: list[AstExprBase] = Field(default_factory=list)
