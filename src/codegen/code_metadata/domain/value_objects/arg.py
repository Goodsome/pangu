from __future__ import annotations
from typing import TYPE_CHECKING
from foundation.building_blocks.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class Arg(ValueObject):
    """Represents a single function/lambda parameter."""

    arg: str
    annotation: AstExpr | None = None
