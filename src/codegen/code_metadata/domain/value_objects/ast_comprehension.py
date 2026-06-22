from __future__ import annotations
from typing import TYPE_CHECKING
from pydantic import Field
from foundation.building_blocks.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstComprehension(ValueObject):
    target: AstExpr
    iter: AstExpr
    ifs: list[AstExpr] = Field(default_factory=list)
    is_async: int = 0
