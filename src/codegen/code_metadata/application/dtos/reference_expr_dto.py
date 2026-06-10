from __future__ import annotations
from pydantic import BaseModel
from typing import TYPE_CHECKING
from typing import Literal
from codegen.code_metadata.domain.enums.expr_kind import ExprKind

if TYPE_CHECKING:
    from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr


class ReferenceExprDto(BaseModel):
    kind: Literal[ExprKind.REFERENCE] = ExprKind.REFERENCE
    target: str
    source: ParsedExpr | ReferenceExprDto | None
