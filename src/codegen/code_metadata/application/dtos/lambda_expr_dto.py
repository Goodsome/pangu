from __future__ import annotations
from typing import TYPE_CHECKING
from typing_extensions import Literal
from pydantic import BaseModel
from pydantic import Field
from codegen.code_metadata.domain.enums.expr_kind import ExprKind

if TYPE_CHECKING:
    from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr


class LambdaExprDto(BaseModel):
    kind: Literal[ExprKind.LAMBDA] = ExprKind.LAMBDA
    params: list[str] = Field(default_factory=list)
    body: ParsedExpr
