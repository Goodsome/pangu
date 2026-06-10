from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Annotated
from typing import Literal
from typing import Optional
from pydantic import Field
from pydantic import TypeAdapter
from codegen.code_metadata.domain.enums.ast_type_param_kind import AstTypeParamKind
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.ast_expr import AstExpr


class AstTypeVar(ValueObject):
    """Represents a TypeVar type parameter (e.g., T, T: int, T: int = str)."""

    kind: Literal[AstTypeParamKind.TYPE_VAR] = AstTypeParamKind.TYPE_VAR
    name: str
    bound: Optional[AstExpr] = None
    default_value: Optional[AstExpr] = None


class AstTypeVarTuple(ValueObject):
    """Represents a TypeVarTuple type parameter (e.g., *Ts, *Ts = int)."""

    kind: Literal[AstTypeParamKind.TYPE_VAR_TUPLE] = AstTypeParamKind.TYPE_VAR_TUPLE
    name: str
    default_value: Optional[AstExpr] = None


class AstParamSpec(ValueObject):
    """Represents a ParamSpec type parameter (e.g., **P, **P = [int, str])."""

    kind: Literal[AstTypeParamKind.PARAM_SPEC] = AstTypeParamKind.PARAM_SPEC
    name: str
    default_value: Optional[AstExpr] = None


AstTypeParam = Annotated[
    AstTypeVar | AstTypeVarTuple | AstParamSpec, Field(discriminator="kind")
]
type_param_adapter: TypeAdapter[AstTypeParam] = TypeAdapter(AstTypeParam)
