from typing import TYPE_CHECKING
from pydantic import Field
from typing_extensions import Literal
from codegen.shared.domain.core.value_object import ValueObject
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.expr_def import ExprDef


class SequenceExpr(ValueObject):
    """描述容器字面量，例如: [1, 2, 3] 或 {"a": 1} (对应 ast.List, ast.Dict 等)"""

    kind: Literal[ExprKind.SEQUENCE] = ExprKind.SEQUENCE
    container_type: Literal["list", "tuple", "set"]
    elements: list["ExprDef"] = Field(default_factory=list)

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        for element in self.elements:
            result.update(element.get_component_ids())
        return result
