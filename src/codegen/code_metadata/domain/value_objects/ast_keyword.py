from __future__ import annotations
from typing import TYPE_CHECKING
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstKeyword(ValueObject):
    arg: str | None
    value: AstExpr
