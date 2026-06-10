from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.expr_def import ExprDef


class LambdaExpr(ValueObject):
    """描述 lambda 表达式，例如: lambda x, y: x + y (对应 ast.Lambda)"""

    kind: Literal[ExprKind.LAMBDA] = ExprKind.LAMBDA
    params: list[str] = Field(default_factory=list)
    body: "ExprDef"

    def get_component_ids(self) -> set[ComponentId]:
        return self.body.get_component_ids()
