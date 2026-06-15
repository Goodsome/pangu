from __future__ import annotations
from typing import Literal
from pydantic import Field
from typing_extensions import TYPE_CHECKING
from codegen.code_metadata.domain.enums.expr_kind import ExprKind
from codegen.code_metadata.domain.identifiers.component_id import ComponentId
from codegen.code_metadata.domain.value_objects.reference_target import ReferenceTarget
from codegen.shared.domain.core.value_object import ValueObject

if TYPE_CHECKING:
    from codegen.code_metadata.domain.value_objects.expr_def import ExprDef


class ReferenceExpr(ValueObject):
    """核心设计：描述对变量/标识符的引用 (对应 ast.Name 或 ast.Attribute) 在这里完成从代码文本到领域 ID 的深度解析"""

    kind: Literal[ExprKind.REFERENCE] = ExprKind.REFERENCE
    target: ReferenceTarget
    source: ExprDef | None = Field(default=None)

    def get_component_ids(self) -> set[ComponentId]:
        result: set[ComponentId] = set()
        if self.target.component_id:
            result.add(self.target.component_id)
        if self.source:
            result.update(self.source.get_component_ids())
        return result
