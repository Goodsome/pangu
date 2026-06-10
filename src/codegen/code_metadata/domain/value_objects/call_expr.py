from typing import TYPE_CHECKING
from typing import Literal
from pydantic import Field
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.expr_def import ExprDef


class CallExpr(ValueObject):
    """描述函数或类实例化调用，例如: Field(default_factory=list) (对应 ast.Call)"""

    kind: Literal[ExprKind.CALL] = ExprKind.CALL
    callee: "ExprDef"
    args: list["ExprDef"] = Field(default_factory=list)
    kwargs: dict[str, "ExprDef"] = Field(default_factory=dict)

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        result.update(self.callee.get_component_ids())
        for arg in self.args:
            result.update(arg.get_component_ids())
        for kwarg in self.kwargs.values():
            result.update(kwarg.get_component_ids())
        return result
