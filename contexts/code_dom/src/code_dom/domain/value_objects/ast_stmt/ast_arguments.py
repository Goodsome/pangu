from __future__ import annotations
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from typing import Optional
from pydantic import Field
from foundation.building_blocks.value_object import ValueObject
from code_dom.domain.value_objects.ast_expr.ast_lambda import Arg


class AstArguments(ValueObject):
    """Represents function/lambda arguments."""

    posonlyargs: list[Arg] = Field(default_factory=list)
    args: list[Arg] = Field(default_factory=list)
    vararg: Optional[Arg] = None
    kwonlyargs: list[Arg] = Field(default_factory=list)
    kw_defaults: list[Optional[AstExprBase]] = Field(default_factory=list)
    kwarg: Optional[Arg] = None
    defaults: list[AstExprBase] = Field(default_factory=list)
