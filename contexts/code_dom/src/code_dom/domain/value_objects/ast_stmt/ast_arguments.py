from __future__ import annotations

from pydantic import Field

from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from code_dom.domain.value_objects.ast_expr.ast_lambda import Arg
from foundation.building_blocks.value_object import ValueObject


class AstArguments(ValueObject):
    """Represents function/lambda arguments."""

    posonlyargs: list[Arg] = Field(default_factory=list)
    args: list[Arg] = Field(default_factory=list)
    vararg: Arg | None = None
    kwonlyargs: list[Arg] = Field(default_factory=list)
    kw_defaults: list[AstExprBase | None] = Field(default_factory=list)
    kwarg: Arg | None = None
    defaults: list[AstExprBase] = Field(default_factory=list)
