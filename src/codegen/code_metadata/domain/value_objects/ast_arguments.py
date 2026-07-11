from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
from pydantic import Field
from foundation.building_blocks.value_object import ValueObject
from codegen.code_metadata.domain.value_objects.ast_expr.ast_lambda import Arg

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstArguments(ValueObject):
    """Represents function/lambda arguments."""

    posonlyargs: list[Arg] = Field(default_factory=list)
    args: list[Arg] = Field(default_factory=list)
    vararg: Optional[Arg] = None
    kwonlyargs: list[Arg] = Field(default_factory=list)
    kw_defaults: list[Optional[AstExpr]] = Field(default_factory=list)
    kwarg: Optional[Arg] = None
    defaults: list[AstExpr] = Field(default_factory=list)
