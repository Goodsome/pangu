from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.ast_expr_kind import AstExprKind
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstJoinedStr(ValueObject):
    kind: Literal[AstExprKind.JOINED_STR] = AstExprKind.JOINED_STR
    values: list[AstExpr] = Field(default_factory=list)
