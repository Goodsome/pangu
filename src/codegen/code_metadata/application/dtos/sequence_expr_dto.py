from __future__ import annotations
from typing import TYPE_CHECKING
from pydantic import BaseModel
from pydantic import Field
from typing_extensions import Literal
from codegen.code_metadata.domain.enums.expr_kind import ExprKind

if TYPE_CHECKING:
    from codegen.code_metadata.application.dtos.parsed_expr import ParsedExpr


class SequenceExprDto(BaseModel):
    """描述容器字面量，例如: [1, 2, 3] 或 {"a": 1} (对应 ast.List, ast.Dict 等)"""

    kind: Literal[ExprKind.SEQUENCE] = ExprKind.SEQUENCE
    container_type: Literal["list", "tuple", "set"]
    elements: list[ParsedExpr] = Field(default_factory=list)
