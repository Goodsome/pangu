from code_dom.domain.enums.ast_expr_kind import AstExprKind
from code_dom.domain.value_objects.ast_expr.ast_expr_base import (
    AstExprBase,
)
from dataclasses import dataclass, field
from foundation.building_blocks.value_object import ValueObject
from typing import Literal


class AstLambda(AstExprBase):
    kind: Literal[AstExprKind.LAMBDA] = AstExprKind.LAMBDA
    args: LambdaArgs
    body: AstExprBase


@dataclass
class LambdaArgs:
    """Represents the parameter specification of a lambda (mirrors ast.arguments)."""

    posonlyargs: list[Arg] = field(default_factory=list)
    args: list[Arg] = field(default_factory=list)
    vararg: Arg | None = None
    kwonlyargs: list[Arg] = field(default_factory=list)
    kw_defaults: list[str | None] = field(default_factory=list)
    kwarg: Arg | None = None
    defaults: list[str | None] = field(default_factory=list)


class Arg(ValueObject):
    """Represents a single function/lambda parameter."""

    arg: str
    annotation: AstExprBase | None = None
