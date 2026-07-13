from __future__ import annotations

from typing import Annotated, Literal

from pydantic import Field, TypeAdapter

from code_dom.domain.enums.ast_type_param_kind import AstTypeParamKind
from code_dom.domain.value_objects.ast_expr.ast_expr_base import AstExprBase
from foundation.building_blocks.value_object import ValueObject


class AstTypeVar(ValueObject):
    """Represents a TypeVar type parameter (e.g., T, T: int, T: int = str)."""

    kind: Literal[AstTypeParamKind.TYPE_VAR] = AstTypeParamKind.TYPE_VAR
    name: str
    bound: AstExprBase | None = None
    default_value: AstExprBase | None = None


class AstTypeVarTuple(ValueObject):
    """Represents a TypeVarTuple type parameter (e.g., *Ts, *Ts = int)."""

    kind: Literal[AstTypeParamKind.TYPE_VAR_TUPLE] = AstTypeParamKind.TYPE_VAR_TUPLE
    name: str
    default_value: AstExprBase | None = None


class AstParamSpec(ValueObject):
    """Represents a ParamSpec type parameter (e.g., **P, **P = [int, str])."""

    kind: Literal[AstTypeParamKind.PARAM_SPEC] = AstTypeParamKind.PARAM_SPEC
    name: str
    default_value: AstExprBase | None = None


AstTypeParam = Annotated[
    AstTypeVar | AstTypeVarTuple | AstParamSpec, Field(discriminator="kind")
]
type_param_adapter: TypeAdapter[AstTypeParam] = TypeAdapter(AstTypeParam)
